import importlib
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from PIL import Image

from editorial.backend import ServiceError, optimize_image

publishing = importlib.import_module("api.publishing")
ADMIN = "c7000000-0000-4000-a000-000000000001"
CATEGORY = "c7000000-0000-4000-a000-000000000002"
ARTICLE = "c7000000-0000-4000-a000-000000000003"


class ProviderFixture:
    """Test-only provider. Production always constructs the real REST client."""
    ready = True
    auth_ready = True
    admin_ids = {ADMIN}

    def __init__(self):
        self.sessions = {}
        self.rows = {}
        self.cats = {CATEGORY: {"id": CATEGORY, "name": "Artificial Intelligence", "section": "ai"}}
        self.images = {}
        self.version = 0

    def login(self, email, password):
        if password != "test-only":
            raise ServiceError(400)
        return {"user": {"id": ADMIN if email == "editor@example.test" else "not-authorized"},
                "access_token": "provider-token", "expires_in": 3600}

    def user(self, token):
        return {"id": ADMIN} if token == "provider-token" else {}

    def image(self, image_id, method="GET", data=None):
        if method == "POST":
            self.images[image_id] = data
        elif method == "DELETE":
            self.images.pop(image_id, None)
        else:
            return self.images[image_id]

    def articles(self, *, published=False):
        return [dict(row, category=self.cats[row["category_id"]])
                for row in self.rows.values() if not published or row["status"] == "published"]

    def table(self, name, method="GET", *, query=None, data=None):
        query = query or {}
        if name == "sessions":
            key = query.get("digest", "")[3:]
            if method == "POST":
                self.sessions[data["digest"]] = data
            elif method == "DELETE":
                self.sessions.pop(key, None)
            return [self.sessions[key]] if key in self.sessions else []
        if name == "categories":
            if method == "POST":
                self.cats["added"] = dict(data, id="added")
            elif method == "PATCH":
                self.cats[query["id"][3:]].update(data)
            return list(self.cats.values())
        if method == "POST":
            self.rows[ARTICLE] = dict(data, id=ARTICLE, status="draft", created_at="2026-12-01T10:00:00+00:00",
                                      published_at=None)
        if method in {"POST", "PATCH"}:
            if method == "PATCH" and query["updated_at"] != "eq." + self.rows[ARTICLE]["updated_at"]:
                return []
            self.version += 1
            self.rows[ARTICLE].update(data, updated_at=f"2026-12-01T10:00:{self.version:02d}+00:00")
            if data.get("status") == "published" and not self.rows[ARTICLE]["published_at"]:
                self.rows[ARTICLE]["published_at"] = self.rows[ARTICLE]["updated_at"]
        rows = self.articles()
        if "id" in query:
            rows = [row for row in rows if query["id"] == "eq." + row["id"]]
        if "image_key" in query:
            rows = [row for row in rows if query["image_key"] == "eq." + (row["image_key"] or "")
                    and (not query.get("status") or row["status"] == "published")]
        if method == "DELETE":
            self.rows.pop(ARTICLE, None)
        return rows


class PublishingTest(unittest.TestCase):
    def setUp(self):
        self.service = ProviderFixture()
        mock_backend = patch.object(publishing, "Backend", return_value=self.service)
        mock_backend.start()
        self.addCleanup(mock_backend.stop)
        self.cookie = ""

    def request(self, path, form=None, *, cookie=None, origin=None, upload=None):
        captured = {}
        content_type = "application/x-www-form-urlencoded"
        payload = urlencode(form or {}).encode()
        if upload is not None:
            boundary = "test-boundary"
            parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()
                     for key, value in form.items()]
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="cover.png"\r\n'
                         'Content-Type: image/png\r\n\r\n'.encode() + upload + b"\r\n")
            payload = b"".join(parts) + f"--{boundary}--\r\n".encode()
            content_type = f"multipart/form-data; boundary={boundary}"

        def start(status, headers):
            captured.update(status=int(status.split()[0]), headers=dict(headers))

        body = b"".join(publishing.app({
            "PATH_INFO": path.partition("?")[0], "QUERY_STRING": path.partition("?")[2],
            "REQUEST_METHOD": "GET" if form is None else "POST",
            "HTTP_ORIGIN": publishing.ORIGIN if origin is None else origin,
            "HTTP_COOKIE": self.cookie if cookie is None else cookie,
            "CONTENT_LENGTH": str(len(payload)), "CONTENT_TYPE": content_type, "wsgi.input": BytesIO(payload),
        }, start))
        return captured["status"], captured["headers"], body

    def signin(self):
        status, headers, _ = self.request("/admin/login/", {"email": "editor@example.test", "password": "test-only"})
        self.assertEqual(status, 303)
        self.assertIn("Secure; HttpOnly; SameSite=Strict", headers["Set-Cookie"])
        self.cookie = headers["Set-Cookie"].split(";")[0]

    def test_authorization_and_logout(self):
        self.assertEqual(self.request("/admin/")[0], 303)
        self.assertEqual(self.request("/admin/articles/new/", {})[0], 303)
        self.assertEqual(self.request("/api/publishing?route=/admin/categories/", {})[0], 303)
        self.assertEqual(self.request("/admin/login/", {"email": "visitor@example.test", "password": "test-only"})[0], 401)
        self.signin()
        self.assertEqual(self.request("/admin/")[0], 200)
        self.assertEqual(self.request("/admin/categories/", {"name": "X"}, origin="https://elsewhere.test")[0], 403)
        self.assertEqual(self.request("/admin/logout/", {})[0], 303)
        self.assertEqual(self.request("/admin/")[0], 303)

    def test_article_lifecycle_and_cover_privacy(self):
        self.signin()
        form = {
            "title": "Workflow test article", "slug": "workflow-test-article", "summary": "Only a test",
            "author": "Test author", "body": '## Topic\n\n<script>alert(1)</script>\n\n'
            '[Open](javascript:alert)\n\n## Heading {onclick="bad()"}\n\n```text\nexample\n```',
            "category_id": CATEGORY, "image_alt": "A test pixel",
        }
        buffer = BytesIO()
        Image.new("RGB", (10, 10)).save(buffer, "PNG")
        self.assertEqual(self.request("/admin/articles/new/", form, upload=buffer.getvalue())[0], 303)
        editor = f"/admin/articles/{ARTICLE}/"
        public = "/blog/workflow-test-article/"
        image = self.service.rows[ARTICLE]["image_key"]
        media = f"/media/{image}.webp"
        self.assertEqual(self.request(public)[0], 404)
        self.assertNotIn(b"Workflow test article", self.request("/")[2])
        self.assertEqual(self.request(media)[0], 404)
        self.assertEqual(self.request("/admin" + media, cookie="")[0], 404)
        self.assertEqual(self.request("/admin" + media)[1]["Content-Type"], "image/webp")
        self.assertEqual(self.request(editor + "preview/", cookie="")[0], 303)
        preview = self.request(editor + "preview/")[2]
        self.assertIn(b"Workflow test article", preview)
        self.assertNotIn(b"<script>alert(1)</script>", preview)
        self.assertNotIn(b'href="javascript:', preview)
        class EventAttributes(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag in {"h2", "a", "img"}:
                    for name, _ in attrs:
                        if name.startswith("on"):
                            raise AssertionError(f"Unsafe attribute: {name}")

        EventAttributes().feed(preview.decode())
        form.update(version=self.service.rows[ARTICLE]["updated_at"], title="Updated workflow test article")
        self.assertEqual(self.request(editor, form)[0], 303)
        self.assertEqual(self.request(editor, form)[0], 400)

        def transition(status):
            return self.request(editor + "transition/", {"status": status, "version": self.service.rows[ARTICLE]["updated_at"]})

        self.assertEqual(transition("published")[0], 400)
        self.assertEqual(transition("review")[0], 303)
        self.assertEqual(self.request(public)[0], 404)
        self.assertEqual(transition("published")[0], 303)
        self.assertEqual(self.request(public)[0], 200)
        self.assertEqual(self.request("/api/publishing?route=" + public)[0], 200)
        self.assertEqual(self.request(media)[0], 200)
        self.assertIn(b"Updated workflow test article", self.request("/")[2])
        self.assertIn(b"/blog/workflow-test-article/", self.request("/sitemap.xml")[2])
        self.assertEqual(self.request(editor + "delete/")[0], 409)
        self.assertEqual(transition("draft")[0], 303)
        self.assertEqual(self.request(public)[0], 404)
        self.assertEqual(self.request(media)[0], 404)
        self.assertIn(b"Delete permanently", self.request(editor + "delete/")[2])
        self.assertEqual(self.request(editor + "delete/", {"version": self.service.rows[ARTICLE]["updated_at"]})[0], 303)
        self.assertNotIn(image, self.service.images)

    def test_category_management_and_legacy_site(self):
        self.signin()
        self.assertEqual(self.request("/admin/categories/", {"name": "Devices", "section": "gadgets"})[0], 303)
        self.assertIn(b"Devices", self.request("/admin/categories/")[2])
        self.assertEqual(self.request("/admin/categories/", {"id": CATEGORY, "name": "AI Coverage"})[0], 303)
        self.assertIn(b"AI Coverage", self.request("/admin/categories/")[2])
        home = self.request("/")[2].decode()
        baseline = Path("index.html").read_text()
        self.assertEqual(home, baseline.replace("<!-- Generated by scripts/build.py -->\n", ""))
        self.assertEqual(self.request("/blog/when-my-homelab-started-feeling-like-a-platform/")[0], 200)

    def test_upload_validation_and_unconfigured_service(self):
        with self.assertRaises(ValueError):
            optimize_image(b"<svg/>")
        self.service.ready = self.service.auth_ready = False
        self.assertEqual(self.request("/admin/")[0], 503)
        self.assertEqual(self.request("/")[0], 200)


if __name__ == "__main__":
    unittest.main()
