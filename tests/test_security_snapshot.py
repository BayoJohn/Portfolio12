from unittest import TestCase

from scripts import build


class SecuritySnapshotTest(TestCase):
    def test_exploitation_and_severity_are_independent(self):
        record = {
            "id": "fixture",
            "vendor": "Fixture vendor",
            "product": "Fixture product",
            "description": "Test record",
            "published": "2026-01-01",
            "action": "Follow official guidance.",
            "advisory": "https://example.test/fixture",
        }
        snapshot = {"checked": "2026-01-02", "records": [
            {**record, "id": "scored", "cvss": 9.8, "cvss_version": "CVSS v3", "score_source": "Fixture"},
            {**record, "id": "exploited", "vendor": "Another vendor", "product": "Another product",
             "kev_added": "2026-01-02", "exploitation_source": "https://example.test/catalogue"},
        ]}
        html = build.vulnerability_table(snapshot)
        self.assertIn('data-severity="Critical" data-exploitation="Unknown"', html)
        self.assertIn('data-severity="Unscored" data-exploitation="Known exploited"', html)
        for name in ("severity", "vendor", "product", "exploitation"):
            self.assertIn(f'<select name="{name}">', html)

    def test_no_data_has_no_alerts_or_filters(self):
        self.assertEqual(build.security_alerts([]), "")
        self.assertNotIn("<select", build.vulnerability_table({"records": []}))
        self.assertIn("official CISA catalogue", build.security_records([]))
