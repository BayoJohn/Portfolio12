"""Regression checks for public correction notes on Markdown articles."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts import build


class ArticleCorrectionsTest(TestCase):
    def load_post(self, corrections):
        front_matter = {
            "title": "Fixture article",
            "category": "Technology",
            "excerpt": "A fixture for correction rendering.",
            "dateTime": "2026-11-20",
            "updatedTime": "2026-11-21",
            "corrections": corrections,
        }
        with TemporaryDirectory() as directory, patch.object(build, "ROOT", Path(directory)):
            posts = Path(directory) / "content" / "blog"
            posts.mkdir(parents=True)
            (posts / "fixture.md").write_text(
                f"---\n{json.dumps(front_matter)}\n---\n\nFixture text.\n", encoding="utf-8"
            )
            return build.read_posts("blog")[0]

    def test_order_escaping_and_modified_date(self):
        post = self.load_post([
            {"date": "2026-11-21", "note": "First correction."},
            {"date": "2026-11-23", "note": "<unsafe> second correction."},
        ])
        self.assertEqual(post["updatedTime"], "2026-11-23")
        markup = build.article_corrections(post)
        self.assertLess(markup.index("second correction"), markup.index("First correction"))
        self.assertIn("&lt;unsafe&gt;", markup)
        self.assertNotIn("<unsafe>", markup)
        self.assertIn("blog%2Ffixture%2F", markup)
        self.assertIn('"dateModified": "2026-11-23"', build.metadata(post["url"], post["title"], post["excerpt"], post))

    def test_correction_cannot_precede_publication(self):
        with self.assertRaisesRegex(ValueError, "on or after publication"):
            self.load_post([{"date": "2026-11-19", "note": "Invalid date."}])
