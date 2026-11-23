"""Server-only Supabase REST client and upload validation."""
import json
import os
from datetime import datetime, timezone
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError


class ServiceError(Exception):
    def __init__(self, status):
        self.status = status


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = build_opener(NoRedirect())
MAX_IMAGE = 2_800_000


def now():
    return datetime.now(timezone.utc)


class Backend:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.public_key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
        self.secret = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        self.admin_ids = set(os.environ.get("EDITORIAL_ADMIN_IDS", "").replace(" ", "").split(","))
        parsed = urlsplit(self.url)
        self.ready = bool(parsed.scheme == "https" and parsed.hostname and not parsed.path and
                          not parsed.username and not parsed.query and not parsed.fragment and self.secret)
        self.auth_ready = self.ready and bool(self.public_key and self.admin_ids - {""})

    def request(self, path, method="GET", *, data=None, key=None, token=None, binary=False):
        if not self.ready:
            raise ServiceError(503)
        headers = {"apikey": key or self.secret}
        if token or not key:
            # Legacy service-role JWTs use Authorization. New server secrets use apikey.
            bearer = token or (self.secret if self.secret.startswith("ey") else "")
            if bearer:
                headers["Authorization"] = "Bearer " + bearer
        if data is not None:
            if isinstance(data, bytes):
                headers["Content-Type"] = "image/webp"
            else:
                data = json.dumps(data).encode()
                headers["Content-Type"] = "application/json"
        if path.startswith("/rest/"):
            headers["Prefer"] = "return=representation"
        try:
            with OPENER.open(Request(self.url + path, data=data, headers=headers, method=method), timeout=10) as response:
                payload = response.read()
                return payload if binary else json.loads(payload) if payload else None
        except HTTPError as exc:
            raise ServiceError(exc.code) from None
        except (URLError, TimeoutError, ValueError):
            raise ServiceError(503) from None

    def table(self, name, method="GET", *, query=None, data=None):
        suffix = "?" + urlencode(query) if query else ""
        return self.request("/rest/v1/editorial_" + name + suffix, method, data=data)

    def login(self, email, password):
        return self.request("/auth/v1/token?grant_type=password", "POST",
                            key=self.public_key, data={"email": email, "password": password})

    def user(self, token):
        return self.request("/auth/v1/user", key=self.public_key, token=token)

    def image(self, image_id, method="GET", data=None):
        kind = "authenticated/" if method == "GET" else ""
        return self.request(f"/storage/v1/object/{kind}editorial-images/{image_id}.webp",
                            method, data=data, binary=method == "GET")

    def articles(self, *, published=False):
        query = {"select": "*,category:editorial_categories(name,section)", "order": "created_at.desc,id"}
        if published:
            query.update(status="eq.published", order="published_at.desc,id")
        rows = []
        while True:
            page = self.table("articles", query={**query, "limit": 250, "offset": len(rows)})
            rows.extend(page)
            if not page:
                return rows


def optimize_image(payload):
    if not payload or len(payload) > MAX_IMAGE:
        raise ValueError("Choose an image under 2.8 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(payload), formats=("JPEG", "PNG", "WEBP")) as image:
                if image.width * image.height > 24_000_000 or getattr(image, "is_animated", False):
                    raise ValueError("Choose a still image under 24 megapixels.")
                image = ImageOps.exif_transpose(image)
                image.thumbnail((1800, 1800))
                image = image.convert("RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB")
                output = BytesIO()
                image.save(output, "WEBP", quality=82, method=4)
                if output.tell() > MAX_IMAGE:
                    raise ValueError("The optimized image is too large.")
                return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValueError("Upload a valid JPEG, PNG, or WebP image.") from None
