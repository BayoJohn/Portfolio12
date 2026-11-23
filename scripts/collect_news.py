"""Refresh the public headline index from official RSS feeds."""
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html.parser import HTMLParser
import json
import logging
from pathlib import Path
import re
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

CACHE = Path(__file__).resolve().parents[1] / "assets/data/tech-news.json"
RETENTION = timedelta(days=14)
MAX_BYTES = 2_000_000
MAX_STORIES_PER_SOURCE = 24
TIMEOUT = 8
ATTEMPTS = 2
TOPICS = {
    "artificial intelligence": "Artificial Intelligence",
    "artificial intelligence (ai)": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "cybersecurity": "Cybersecurity",
    "security": "Cybersecurity",
    "computer security": "Cybersecurity",
    "digital security": "Cybersecurity",
    "software": "Software",
    "open source": "Software",
    "gadgets": "Gadgets",
    "startups": "Startups",
    "space technology": "Space Technology",
}


@dataclass(frozen=True)
class Source:
    publisher: str
    feed: str
    domain: str
    default_topic: str


SOURCES = (
    Source("Electronic Frontier Foundation", "https://www.eff.org/rss/updates.xml", "eff.org", "Digital Rights"),
    Source("NASA", "https://www.nasa.gov/technology/feed/", "nasa.gov", "Space Technology"),
)


def publisher_url(value, source):
    """Keep direct publisher links and remove known tracking parameters."""
    if not value or len(value) > 2048 or re.search(r"[\s\\\x00-\x1f\x7f]", value):
        return None
    try:
        parts = urlsplit(value)
        host = parts.hostname
        if (parts.scheme != "https" or not host or parts.username is not None
                or parts.password is not None or parts.port not in (None, 443)
                or not (host == source.domain or host.endswith("." + source.domain))):
            return None
    except ValueError:
        return None
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
             if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"}]
    return urlunsplit(("https", host, parts.path or "/", urlencode(query), ""))


def story_id(url):
    parts = urlsplit(url)
    query = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)))
    key = urlunsplit((parts.scheme, parts.netloc.removeprefix("www."),
                     parts.path.rstrip("/") or "/", query, ""))
    return sha256(key.encode()).hexdigest()


class FeedRedirect(HTTPRedirectHandler):
    max_redirections = 3

    def __init__(self, source):
        self.source = source

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not publisher_url(newurl, self.source):
            raise URLError("Feed redirected outside its approved publisher")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HeadlineText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def headline(value):
    parser = HeadlineText()
    parser.feed(value)
    parser.close()
    return " ".join("".join(parser.parts).split())


def publication_time(value, now):
    try:
        try:
            stamp = parsedate_to_datetime(value)
        except ValueError:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is not None and stamp <= now + timedelta(hours=2):
            return stamp.astimezone(timezone.utc)
    except (ValueError, OverflowError, TypeError):
        pass
    return None


def classify(categories, fallback):
    topics = {TOPICS[category.strip().casefold()] for category in categories
              if category.strip().casefold() in TOPICS}
    return next(iter(topics)) if len(topics) == 1 else fallback


def rss_stories(payload, source, now):
    # These official endpoints use UTF-8. Reject DTDs and oversized responses.
    if len(payload) > MAX_BYTES:
        raise ValueError("Feed exceeds the response size limit")
    text = payload.decode("utf-8-sig")
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.IGNORECASE):
        raise ValueError("Feed has an unsupported DTD")
    channel = ElementTree.fromstring(text).find("channel")
    if channel is None:
        raise ValueError("Expected an RSS channel")
    stories = []
    for item in channel.findall("item")[:100]:
        title = headline(item.findtext("title", ""))
        url = publisher_url(item.findtext("link", "").strip(), source)
        if not title or len(title) > 300 or not url:
            continue
        published = publication_time(item.findtext("pubDate", ""), now)
        stories.append({
            "id": story_id(url),
            "headline": title,
            "publisher": source.publisher,
            "url": url,
            "published_at": published.isoformat() if published else None,
            "category": classify([node.text or "" for node in item.findall("category")], source.default_topic),
            "fetched_at": now.isoformat(),
        })
    return stories


def fetch(source):
    request = Request(source.feed, headers={"User-Agent": "StackedByBayo RSS collector (+https://stackedbybayo.site/)"})
    opener = build_opener(FeedRedirect(source))
    for attempt in range(ATTEMPTS):
        try:
            with opener.open(request, timeout=TIMEOUT) as response:
                return response.read(MAX_BYTES + 1)
        except HTTPError as error:
            if error.code not in {408, 500, 502, 503, 504} or attempt + 1 == ATTEMPTS:
                raise
        except (URLError, TimeoutError, OSError):
            if attempt + 1 == ATTEMPTS:
                raise
        sleep(1)


def read_cache(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["version"] != 1 or not isinstance(data["stories"], list):
            raise ValueError("Unexpected snapshot format")
        return data["stories"]
    except FileNotFoundError:
        return []
    except (ValueError, TypeError, KeyError):
        logging.warning("Ignoring an invalid previous snapshot")
        return []


def merge(previous, fresh, now):
    allowed = {source.publisher: source for source in SOURCES}
    by_id = {}
    first_seen = {}
    for story in [*previous, *fresh]:
        try:
            if publisher_url(story["url"], allowed[story["publisher"]]) != story["url"]:
                continue
            if story["id"] != story_id(story["url"]):
                continue
            fetched = datetime.fromisoformat(story["fetched_at"])
            if fetched.tzinfo is None:
                continue
            first = first_seen.setdefault(story["id"], fetched)
            story = dict(story, fetched_at=first.isoformat())
            age_from = datetime.fromisoformat(story["published_at"]) if story["published_at"] else first
            if age_from >= now - RETENTION:
                by_id[story["id"]] = story
        except (AttributeError, KeyError, TypeError, ValueError):
            continue

    ordered = sorted(by_id.values(), key=lambda story: (
        story["published_at"] is not None,
        story["published_at"] or story["fetched_at"],
        story["id"],
    ), reverse=True)
    counts = {}
    results = []
    for story in ordered:
        publisher = story["publisher"]
        counts[publisher] = counts.get(publisher, 0) + 1
        if counts[publisher] <= MAX_STORIES_PER_SOURCE:
            results.append(story)
    return results


def refresh(path, now=None):
    now = now or datetime.now(timezone.utc).replace(microsecond=0)
    fresh = []
    successes = 0
    for source in SOURCES:
        try:
            stories = rss_stories(fetch(source), source, now)
        except (OSError, ValueError, ElementTree.ParseError) as error:
            logging.warning("%s feed failed (%s)", source.publisher, type(error).__name__)
            continue
        successes += 1
        logging.info("%s supplied %d eligible headlines", source.publisher, len(stories))
        fresh.extend(stories)
    if not successes:
        logging.error("No feed succeeded. Preserving the previous snapshot.")
        return False

    previous = read_cache(path)
    stories = merge(previous, fresh, now)
    if stories != previous or not path.exists():
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps({"version": 1, "stories": stories}, ensure_ascii=True, indent=2) + "\n",
                             encoding="utf-8")
        temporary.replace(path)
    logging.info("%d headlines in the public snapshot", len(stories))
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=CACHE, type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(0 if refresh(args.output) else 1)
