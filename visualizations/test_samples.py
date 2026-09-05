"""Check the publication boundary and reproducible sample export."""
import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import unittest

from build_samples import redact

HERE = Path(__file__).resolve().parent


class SampleTests(unittest.TestCase):
    def test_redaction_keeps_noncredential_query_data(self):
        text, count = redact('https://example.test/data?api_key=fixture-secret&Year=2026 email person@example.test IP 192.0.2.1')
        self.assertEqual(count, 3)
        self.assertNotIn('fixture-secret', text)
        self.assertNotIn('person@example.test', text)
        self.assertNotIn('192.0.2.1', text)
        self.assertIn('&Year=2026', text)

    def test_encoded_and_json_credentials(self):
        text, count = redact('APIKEY%3Dfixture-secret&ok=yes {"password":"fixture-password"} ResourceKey: fixture-resource')
        self.assertEqual(count, 3)
        self.assertNotIn('fixture-', text)
        self.assertIn('&ok=yes', text)

    def test_real_times_and_plain_markup_are_preserved(self):
        fixture = '08:45:55 RCS 1.2 task 123.45 <script>alert("sample")</script>'
        self.assertEqual(redact(fixture), (fixture, 0))

    def test_published_bundle(self):
        packed = json.loads((HERE / 'sample-data.json').read_text())
        raw = gzip.decompress(base64.b64decode(packed['data']))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), packed['sha256'])
        samples = json.loads(raw)
        self.assertEqual(samples['fields'], ['time', 'wiki', 'label', 'page', 'seq', 'excerpt', 'truncated', 'redactions', 'timeGrade'])
        self.assertEqual(len(samples['rows']), 14591)
        self.assertEqual(len({(r[3], r[4]) for r in samples['rows']}), 14591)
        self.assertTrue(all(len(r) == 9 and len(r[5]) <= 1200 for r in samples['rows']))
        chart = json.loads((HERE / 'chart-data.json').read_text())
        self.assertEqual(Counter(chart['wikis'][r[1]] for r in samples['rows']), {'dse':13403,'probier':1013,'fractal':169,'dorfwiki':6})
        self.assertEqual(sum(chart['labels'][r[2]] == '(blank label)' for r in samples['rows']), 899)
        self.assertTrue(all(0 <= r[3] < len(chart['pages']) and 0 <= r[2] < len(chart['labels']) for r in samples['rows']))
        self.assertTrue(all(r[5] == redact(r[5])[0] for r in samples['rows']))


if __name__ == '__main__':
    unittest.main()
