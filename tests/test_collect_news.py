from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from xml.etree.ElementTree import ParseError

from scripts import collect_news as news


NOW = datetime(2026, 11, 23, 12, tzinfo=timezone.utc)
EFF, NASA = news.SOURCES


def rss(url, *, date="Mon, 23 Nov 2026 10:00:00 GMT", categories=""):
    return f"""<rss version="2.0"><channel>
      <item>
        <title>Devices &amp; privacy</title>
        <link>{url}</link><pubDate>{date}</pubDate>{categories}
        <description>Publisher copy that must not appear in the cache.</description>
        <enclosure url="https://example.com/cover.jpg" type="image/jpeg"/>
      </item>
    </channel></rss>""".encode()


class NewsCollectionTest(unittest.TestCase):
    def test_parses_only_headline_metadata_and_uses_explicit_categories(self):
        data = rss("https://www.eff.org/deeplinks/example/?utm_source=feed&amp;page=1",
                   categories="<category>Artificial Intelligence</category>")
        story, = news.rss_stories(data, EFF, NOW)
        self.assertEqual(story["headline"], "Devices & privacy")
        self.assertEqual(story["publisher"], "Electronic Frontier Foundation")
        self.assertEqual(story["url"], "https://www.eff.org/deeplinks/example/?page=1")
        self.assertEqual(story["published_at"], "2026-11-23T10:00:00+00:00")
        self.assertEqual(story["category"], "Artificial Intelligence")
        self.assertEqual(story["fetched_at"], NOW.isoformat())
        self.assertNotIn("description", story)
        self.assertNotIn("image", story)
        conflicting = "<category>AI</category><category>Security</category>"
        self.assertEqual(news.rss_stories(rss(story["url"], categories=conflicting), EFF, NOW)[0]["category"],
                         "Digital Rights")

    def test_rejects_unsafe_links_dates_and_xml(self):
        for url in ("javascript:alert(1)", "https://eff.org.evil.example/item",
                    "https://user@eff.org/item", "https://eff.org:8443/item"):
            with self.subTest(url=url):
                self.assertEqual(news.rss_stories(rss(url), EFF, NOW), [])
        for date in ("tomorrow", "", "2026-12-01T12:00:00Z", "2026-11-23T10:00:00"):
            with self.subTest(date=date):
                self.assertIsNone(news.rss_stories(rss("https://eff.org/item", date=date), EFF, NOW)[0]["published_at"])
        with self.assertRaises(ValueError):
            news.rss_stories(b'<!DOCTYPE rss [<!ENTITY abuse "value">]><rss/>', EFF, NOW)
        with self.assertRaises(ParseError):
            news.rss_stories(b'<rss><channel>', EFF, NOW)

    def test_deduplicates_tracks_first_fetch_and_culls_expired_items(self):
        previous = news.rss_stories(rss("https://www.eff.org/item/?b=1&amp;a=2"), EFF, NOW)
        later = NOW + timedelta(hours=4)
        fresh = news.rss_stories(rss("https://eff.org/item?a=2&amp;b=1&amp;utm_source=rss"), EFF, later)
        merged = news.merge(previous, fresh, later)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["id"], previous[0]["id"])
        self.assertEqual(merged[0]["fetched_at"], NOW.isoformat())
        self.assertEqual(news.merge(merged, [], NOW + timedelta(days=15)), [])

    def test_fetch_retries_transient_errors_and_bounds_reads(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b"<rss/>"
        opener = Mock()
        opener.open.side_effect = [URLError("temporary failure"), response]
        with patch.object(news, "build_opener", return_value=opener), patch.object(news, "sleep"):
            self.assertEqual(news.fetch(EFF), b"<rss/>")
        self.assertEqual(opener.open.call_count, 2)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], news.TIMEOUT)
        response.read.assert_called_once_with(news.MAX_BYTES + 1)

        opener.reset_mock()
        opener.open.side_effect = HTTPError(EFF.feed, 403, "forbidden", {}, None)
        with patch.object(news, "build_opener", return_value=opener), self.assertRaises(HTTPError):
            news.fetch(EFF)
        self.assertEqual(opener.open.call_count, 1)

    def test_partial_outage_keeps_previous_stories_total_outage_keeps_snapshot(self):
        eff = rss("https://www.eff.org/story")
        nasa = rss("https://www.nasa.gov/story")
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tech-news.json"
            with patch.object(news, "fetch", side_effect=[eff, nasa]):
                self.assertTrue(news.refresh(path, NOW))
            original = path.read_bytes()
            with patch.object(news, "fetch", side_effect=[URLError("offline"), nasa]):
                self.assertTrue(news.refresh(path, NOW + timedelta(hours=4)))
            self.assertEqual(path.read_bytes(), original)
            with patch.object(news, "fetch", side_effect=URLError("offline")):
                self.assertFalse(news.refresh(path, NOW + timedelta(hours=8)))
            self.assertEqual(path.read_bytes(), original)

    def test_empty_rss_preserves_an_honest_empty_snapshot(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tech-news.json"
            with patch.object(news, "fetch", return_value=b"<rss><channel /></rss>"):
                self.assertTrue(news.refresh(path, NOW))
            self.assertEqual(news.read_cache(path), [])
