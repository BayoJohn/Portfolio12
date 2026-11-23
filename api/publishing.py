"""Vercel WSGI entry point for the existing publication and private editorial routes."""
from datetime import date, timedelta
from email import policy
from email.parser import BytesParser
from functools import lru_cache
from hashlib import sha256
from http import HTTPStatus
from http.cookies import CookieError, SimpleCookie
import os
import re
from secrets import token_urlsafe
from urllib.parse import parse_qs
from uuid import uuid4

from editorial.backend import Backend, MAX_IMAGE, ServiceError, now, optimize_image
from editorial import views
from scripts import build

SESSION = "__Host-stacked-editor"
ORIGIN = os.environ.get("EDITORIAL_ORIGIN", "https://stackedbybayo.site").rstrip("/")
UUID = r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
ARTICLE_PATH = re.compile(rf"/admin/articles/({UUID}|new)/(preview/|transition/|delete/)?")
MEDIA_PATH = re.compile(rf"/(?:admin/)?media/({UUID})\.webp")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
COLLECTION = {"gadgets": "reviews", "academy": "academy"}


class Rejected(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


def respond(status, body="", kind="text/html; charset=utf-8", headers=()):
    return status, body.encode() if isinstance(body, str) else body, kind, headers


def redirect(path, cookie=None):
    headers = [("Location", path)]
    if cookie is not None:
        headers.append(("Set-Cookie", cookie))
    return respond(303, headers=headers)


def session_cookie(token="", lifetime=0):
    return f"{SESSION}={token}; Path=/; Max-Age={lifetime}; Secure; HttpOnly; SameSite=Strict"


def digest(token):
    return sha256(token.encode("ascii")).hexdigest()


def cookie_token(env):
    try:
        jar = SimpleCookie(env.get("HTTP_COOKIE", ""))
        if SESSION in jar and re.fullmatch(r"[A-Za-z0-9_-]{40,60}", jar[SESSION].value):
            return jar[SESSION].value
    except CookieError:
        pass
    return ""


def admin_session(env, service):
    token = cookie_token(env)
    if not token:
        return None
    rows = service.table("sessions", query={"digest": "eq." + digest(token), "expires_at": "gt." + now().isoformat()})
    if not rows or rows[0]["user_id"] not in service.admin_ids:
        return None
    try:
        profile = service.user(rows[0]["access_token"])
    except ServiceError as error:
        if error.status not in {400, 401, 403}:
            raise
        return None
    return rows[0] if profile.get("id") == rows[0]["user_id"] else None


def fields(env):
    length = env.get("CONTENT_LENGTH") or "0"
    if not length.isascii() or not length.isdecimal() or len(length) > 8 or int(length) > MAX_IMAGE + 650_000:
        raise Rejected(413, "The submitted form is too large.")
    data = env["wsgi.input"].read(int(length))
    content_type = env.get("CONTENT_TYPE", "")
    if content_type.startswith("application/x-www-form-urlencoded"):
        return {name: values[-1] for name, values in parse_qs(data.decode(), keep_blank_values=True, max_num_fields=40).items()}
    if content_type.startswith("multipart/form-data;") and "\n" not in content_type and "\r" not in content_type:
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + data
        )
        if not message.is_multipart() or message.defects:
            raise Rejected(400, "Invalid form upload.")
        result = {}
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if not name or part.is_multipart() or len(result) >= 40:
                raise Rejected(400, "Invalid form upload.")
            content = part.get_payload(decode=True) or b""
            result[name] = content if name == "image" else content.decode("utf-8")
        return result
    raise Rejected(415, "Submit a supported form.")


@lru_cache(maxsize=1)
def legacy_posts():
    return {collection: build.read_posts(collection) for collection in build.COLLECTIONS}


def stored_post(row, *, preview=False):
    category = row["category"]
    published = (row.get("published_at") or row["created_at"])[:10]
    updated = row["updated_at"][:10]
    image = row.get("image_key")
    return {
        "title": row["title"], "url": f'{row["collection"]}/{row["slug"]}/',
        "excerpt": row["summary"], "body": row["body"], "author": row["author"],
        "category": category["name"], "categories": list(dict.fromkeys([category["section"], *row["tags"]])),
        "date": date.fromisoformat(published), "dateTime": published,
        "updatedTime": updated if updated > published else None,
        "articleType": row["article_type"], "seoDescription": row["seo_description"],
        "managed": True,
        "sources": [{"label": "Original source", "url": row["source_url"]}] if row["source_url"] else [],
        "image": f'/{ "admin/" if preview else ""}media/{image}.webp' if image else "",
        "imageAlt": row["image_alt"], "imageCaption": row["image_caption"], "imageCredit": row["image_credit"],
    }


def public_page(path, service):
    if not re.fullmatch(r"/(?:(?:blog|academy|reviews)(?:/[a-z0-9-]+)?/?|(?:search|software)/?|sitemap\.xml)?", path):
        return respond(404, "Page not found", "text/plain; charset=utf-8")
    target = "sitemap.xml" if path == "/sitemap.xml" else path.strip("/") + "/" if path != "/" else ""
    collections = {name: list(posts) for name, posts in legacy_posts().items()}
    # A missing or temporarily unavailable backend cannot take the static publication offline.
    try:
        rows = service.articles(published=True) if service.ready else []
    except ServiceError:
        rows = []
    legacy_urls = {post["url"] for posts in collections.values() for post in posts}
    for row in rows:
        if row["status"] == "published":
            post = stored_post(row)
            if post["url"] not in legacy_urls:
                collections[row["collection"]].append(post)
    for posts in collections.values():
        posts.sort(key=lambda post: post["date"], reverse=True)
    found = {}

    def capture(route, title, description, body, post=None):
        if route in {target, "404.html"}:
            found[route] = build.render_page(route, title, description, body, post)

    urls = build.render_site(collections, capture, target)
    if target == "sitemap.xml":
        return respond(200, build.sitemap(urls), "application/xml; charset=utf-8")
    if target in found:
        return respond(200, found[target])
    return respond(404, found["404.html"])


def category_list(service):
    return service.table("categories", query={"order": "name.asc"})


def single_article(service, article_id):
    rows = service.table("articles", query={
        "id": "eq." + article_id, "select": "*,category:editorial_categories(name,section)"
    })
    if not rows:
        raise Rejected(404, "Article not found.")
    return rows[0]


def login(service, form):
    try:
        email = form.get("email", "")
        password = form.get("password", "")
        if not isinstance(email, str) or not isinstance(password, str) or not 1 <= len(email) <= 320 or not 1 <= len(password) <= 512:
            raise ServiceError(400)
        session = service.login(email, password)
    except ServiceError as error:
        if error.status == 429:
            return respond(429, views.login("Too many attempts. Try again later."))
        if error.status in {400, 401, 403, 422}:
            return respond(401, views.login("Sign-in failed. Check your administrator credentials."))
        raise
    user_id = session.get("user", {}).get("id")
    if user_id not in service.admin_ids:
        return respond(401, views.login("Sign-in failed. Check your administrator credentials."))
    lifetime = min(int(session["expires_in"]), 3600)
    if lifetime <= 0:
        raise Rejected(503, "Administrator sign-in is unavailable.")
    token = token_urlsafe(32)
    service.table("sessions", "DELETE", query={"expires_at": "lt." + now().isoformat()})
    service.table("sessions", "POST", data={
        "digest": digest(token), "user_id": user_id, "access_token": session["access_token"],
        "expires_at": (now() + timedelta(seconds=lifetime)).isoformat(),
    })
    return redirect("/admin/", session_cookie(token, lifetime))


def save_article(service, form, existing, categories):
    row = {}
    for name, label, limit, required in views.FIELDS:
        value = form.get(name, "")
        if not isinstance(value, str) or "\x00" in value or len(value) > limit or (required and not value.strip()):
            raise ValueError(f"Check the {label.lower()} field.")
        row[name] = value.strip()
    if not SLUG.fullmatch(row["slug"]):
        raise ValueError("Use lowercase letters, numbers and single hyphens for the slug.")
    if any(post["url"].split("/")[1] == row["slug"] for posts in legacy_posts().values() for post in posts):
        raise ValueError("An existing article already uses that slug.")
    kind = form.get("article_type", "")
    if kind and kind not in build.ARTICLE_TYPES:
        raise ValueError("Choose a valid article type.")
    if row["source_url"] and not build.web_url(row["source_url"]):
        raise ValueError("Use a complete HTTP or HTTPS source URL.")
    category = next((item for item in categories if item["id"] == form.get("category_id")), None)
    if not category:
        raise ValueError("Choose a valid category.")
    collection = COLLECTION.get(category["section"], "blog")
    if existing.get("published_at") and (row["slug"], collection) != (existing["slug"], existing["collection"]):
        raise ValueError("Published article URLs are permanent. Choose a category in the same collection.")
    row.update(category_id=category["id"], article_type=kind, collection=collection,
               tags=list(dict.fromkeys(tag.strip() for tag in row["tags"].split(",") if tag.strip())))
    previous = existing.get("image_key")
    row["image_key"] = None if form.get("remove_image") == "1" else previous
    upload = form.get("image")
    if upload and not isinstance(upload, bytes):
        raise ValueError("Choose a file for the featured image.")
    if (upload or row["image_key"]) and not row["image_alt"]:
        raise ValueError("Add descriptive alt text for the featured image.")
    if existing and form.get("version") != existing["updated_at"]:
        raise ValueError("This article changed. Reload it before saving.")
    new_image = None
    if upload:
        optimized = optimize_image(upload)
        new_image = str(uuid4())
        service.image(new_image, "POST", optimized)
        row["image_key"] = new_image

    def remove_image(image_id):
        try:
            service.image(image_id, "DELETE")
        except ServiceError:
            pass

    try:
        if existing:
            saved = service.table("articles", "PATCH", query={
                "id": "eq." + existing["id"], "updated_at": "eq." + existing["updated_at"],
            }, data=row)
            if not saved:
                raise ValueError("This article changed. Reload it before saving.")
        else:
            saved = service.table("articles", "POST", data=row)
    except (ServiceError, ValueError) as error:
        # An ambiguous upstream failure may have committed the row. Avoid deleting a cover it could reference.
        if new_image and (isinstance(error, ValueError) or error.status == 409):
            remove_image(new_image)
        if isinstance(error, ServiceError) and error.status == 409:
            raise ValueError("That slug is already used.") from None
        raise
    if previous and previous != row["image_key"]:
        remove_image(previous)
    return saved[0]["id"]


def route_admin(path, method, env, service):
    if not service.auth_ready:
        raise Rejected(503, "The editorial service has not been configured.")
    if path == "/admin/login/":
        return login(service, fields(env)) if method == "POST" else respond(200, views.login())
    session = admin_session(env, service)
    if not session:
        return redirect("/admin/login/", session_cookie())
    if path == "/admin/logout/" and method == "POST":
        service.table("sessions", "DELETE", query={"digest": "eq." + session["digest"]})
        return redirect("/admin/login/", session_cookie())
    if path == "/admin/" and method == "GET":
        return respond(200, views.dashboard(service.articles()))
    if path == "/admin/categories/":
        if method == "POST":
            form = fields(env)
            name = form.get("name", "").strip()
            category_id = form.get("id", "")
            if not 1 <= len(name) <= 80 or "\x00" in name:
                raise Rejected(400, "Enter a valid category name.")
            try:
                if category_id and re.fullmatch(UUID, category_id):
                    service.table("categories", "PATCH", query={"id": "eq." + category_id}, data={"name": name})
                elif not category_id and form.get("section") in views.SECTIONS:
                    service.table("categories", "POST", data={"name": name, "section": form["section"]})
                else:
                    raise Rejected(400, "Choose a valid category or section.")
            except ServiceError as error:
                if error.status != 409:
                    raise
                return respond(409, views.categories_page(category_list(service), "That category name already exists."))
            return redirect(path)
        return respond(200, views.categories_page(category_list(service)))
    if match := ARTICLE_PATH.fullmatch(path):
        article_id, action = match.groups()
        row = single_article(service, article_id) if article_id != "new" else {}
        if action == "preview/" and row and method == "GET":
            post = stored_post(row, preview=True)
            rendered = []

            def capture(route, title, description, body, post=None):
                body = body.replace('href="../"', f'href="/admin/articles/{article_id}/"', 1)
                rendered.append(build.render_page(route, title, description, body, post)
                                .replace('href="../../', 'href="/').replace('src="../../', 'src="/'))

            build.article(post, row["collection"], [post], capture)
            return respond(200, rendered[0], headers=[("X-Robots-Tag", "noindex, nofollow")])
        if action == "transition/" and row and method == "POST":
            form = fields(env)
            target = form.get("status")
            if target not in views.TRANSITIONS[row["status"]]:
                raise Rejected(400, "That publishing transition is unavailable.")
            if form.get("version") != row["updated_at"]:
                raise Rejected(409, "This article changed. Reload it before changing status.")
            saved = service.table("articles", "PATCH", query={
                "id": "eq." + article_id, "updated_at": "eq." + row["updated_at"], "status": "eq." + row["status"],
            }, data={"status": target})
            if not saved:
                raise Rejected(409, "This article changed. Reload it before changing status.")
            return redirect(f"/admin/articles/{article_id}/")
        if action == "delete/" and row:
            if row["status"] == "published":
                raise Rejected(409, "Unpublish this article before deleting it.")
            if method == "GET":
                return respond(200, views.confirm_delete(row))
            form = fields(env)
            if form.get("version") != row["updated_at"]:
                raise Rejected(409, "This article changed. Reload it before deleting.")
            removed = service.table("articles", "DELETE", query={
                "id": "eq." + article_id, "updated_at": "eq." + row["updated_at"], "status": "neq.published",
            })
            if not removed:
                raise Rejected(409, "This article changed. Reload it before deleting.")
            if row["image_key"]:
                try:
                    service.image(row["image_key"], "DELETE")
                except ServiceError:
                    pass
            return redirect("/admin/")
        if action is None:
            categories = category_list(service)
            if method == "POST":
                form = fields(env)
                try:
                    article_id = save_article(service, form, row, categories)
                except ValueError as error:
                    pending = {name: form[name] for name, *_ in views.FIELDS if name in form}
                    pending.update(category_id=form.get("category_id"), article_type=form.get("article_type"))
                    return respond(400, views.editor({**row, **pending}, categories, build.ARTICLE_TYPES, str(error)))
                return redirect(f"/admin/articles/{article_id}/")
            return respond(200, views.editor(row, categories, build.ARTICLE_TYPES))
    raise Rejected(404, "Editorial page not found.")


def route(env, path, method, service):
    private = path.startswith("/admin/")
    if method == "POST":
        if not private:
            raise Rejected(405, "Method not allowed.")
        if env.get("HTTP_ORIGIN") != ORIGIN:
            raise Rejected(403, "Submit this form from the publication’s own domain.")
    if match := MEDIA_PATH.fullmatch(path):
        if method != "GET":
            raise Rejected(405, "Method not allowed.")
        image_id = match[1]
        query = {"image_key": "eq." + image_id, "select": "id"}
        if private:
            if not service.auth_ready or not admin_session(env, service):
                raise Rejected(404, "Image not found.")
        else:
            if not service.ready:
                raise Rejected(404, "Image not found.")
            query["status"] = "eq.published"
        if not service.table("articles", query=query):
            raise Rejected(404, "Image not found.")
        return respond(200, service.image(image_id), "image/webp")
    if private:
        return route_admin(path, method, env, service)
    return public_page(path, service)


def app(env, start_response):
    path = env.get("PATH_INFO", "/")
    method = env.get("REQUEST_METHOD", "GET")
    if path.rstrip("/") in {"/api/publishing", "/api/publishing.py"}:
        # Vercel passes the original path through the internal rewrite query.
        options = parse_qs(env.get("QUERY_STRING", ""), keep_blank_values=True).get("route", [])
        path = options[0] if options else "-"
        path = "/" if path == "/" else path.rstrip("/") + ("" if path.endswith((".webp", ".xml")) else "/")
    if (path == "/admin" or path.startswith("/admin/")) and not path.endswith(("/", ".webp")):
        path += "/"
    private = path.startswith("/admin/")
    try:
        if method not in {"GET", "POST", "HEAD"}:
            raise Rejected(405, "Method not allowed.")
        if len(path) > 250:
            raise Rejected(404, "Page not found.")
        result = route(env, path, "GET" if method == "HEAD" else method, Backend())
    except Rejected as error:
        result = respond(error.status, views.layout("Request unavailable", f"<p>{views.text(error.message)}</p>")
                         if private else error.message, "text/html; charset=utf-8" if private else "text/plain; charset=utf-8")
    except ServiceError as error:
        status = 404 if error.status == 404 and "/media/" in path else 503
        result = respond(status, "The editorial service is temporarily unavailable.", "text/plain; charset=utf-8")
    except (ValueError, KeyError, TypeError):
        result = respond(400, "Invalid request.", "text/plain; charset=utf-8")
    status, body, kind, headers = result
    security = [("Content-Type", kind), ("Cache-Control", "private, no-store"),
                ("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "same-origin")]
    if private:
        security.extend([
            ("X-Frame-Options", "DENY"), ("X-Robots-Tag", "noindex, nofollow"),
            ("Content-Security-Policy", "default-src 'self'; script-src 'none'; style-src 'self' https://fonts.googleapis.com; "
             "font-src 'self' https://fonts.gstatic.com; img-src 'self' https:; frame-ancestors 'none'; "
             "base-uri 'none'; object-src 'none'; form-action 'self'"),
        ])
    start_response(f"{status} {HTTPStatus(status).phrase}", [*security, *headers])
    return [b"" if method == "HEAD" else body]
