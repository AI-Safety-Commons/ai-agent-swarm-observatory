"""Build the public static dashboard from the committed aggregate dataset."""
import json
import base64
import gzip
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "visualizations"
data = (SOURCE / "chart-data.json").read_text(encoding="utf-8")
parsed = json.loads(data)
totals = [sum(row[5] for row in parsed["rows"] if row[2] == i) for i in range(4)]
assert totals == [14591, 5217, 101, 4], totals
assert sum(row[3] for row in parsed["recreations"]) == 68
for char, escape in [("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026")]:
    data = data.replace(char, escape)
template = (SOURCE / "wiki-activity.template.html").read_text(encoding="utf-8")
assert template.count("__CHART_DATA__") == 1
fragment = template.replace("__CHART_DATA__", data)
samples = (SOURCE / "sample-data.json").read_text(encoding="utf-8")
packed = json.loads(samples)
raw_samples = gzip.decompress(base64.b64decode(packed['data'], validate=True))
assert hashlib.sha256(raw_samples).hexdigest() == packed['sha256']
sample_data = json.loads(raw_samples)
assert len(sample_data['rows']) == packed['count'] == 14591
dictionary = json.dumps([parsed[k] for k in ['wikis', 'labels', 'pages']], ensure_ascii=False, separators=(',', ':')).encode()
assert hashlib.sha256(dictionary).hexdigest() == sample_data['dictionarySha256'], 'Regenerate samples after changing chart dictionaries'
assert fragment.count('__SAMPLE_DATA__') == 1
fragment = fragment.replace('__SAMPLE_DATA__', samples)
summary_text = (SOURCE / 'user-summaries.json').read_text(encoding='utf-8')
summaries = json.loads(summary_text)
assert summaries['chartSha256'] == hashlib.sha256((SOURCE / 'chart-data.json').read_bytes()).hexdigest(), 'Review summaries after changing chart data'
named_counts = {}
named_pages = {}
for row in parsed['rows']:
    name = parsed['labels'][row[3]]
    if row[2] == 0 and name != '(blank label)':
        named_counts[name] = named_counts.get(name, 0) + row[5]
        named_pages.setdefault(name, set()).add(row[4])
expected_top = sorted(named_counts, key=lambda n: (-named_counts[n], n))[:20]
assert [s['label'] for s in summaries['summaries']] == expected_top
known_samples = {(parsed['pages'][r[3]], r[4]): r for r in sample_data['rows']}
for summary in summaries['summaries']:
    assert summary['saved_revisions'] == named_counts[summary['label']]
    assert summary['page_count'] == len(named_pages[summary['label']])
    assert summary['paragraph'].strip() and '\n' not in summary['paragraph']
    assert len(summary['evidence']) == 3
    for e in summary['evidence']:
        record = known_samples[(e['page'], e['seq'])]
        assert parsed['labels'][record[2]] == summary['label'] and record[0] == e['time']
for char, escape in [("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026")]:
    summary_text = summary_text.replace(char, escape)
assert fragment.count('__SUMMARY_DATA__') == 1
fragment = fragment.replace('__SUMMARY_DATA__', summary_text)
# Keep the assembled source fragment styled consistently with the public page.
fragment = "<style>\n" + (SOURCE / "dashboard.css").read_text() + "\n</style>\n" + fragment
# This is a standalone public page, not an inline visualization fragment.
assert len(fragment.encode("utf-8")) < 5_000_000
(SOURCE / "wiki-activity.html").write_text(fragment, encoding="utf-8")
subprocess.run([sys.executable, str(SOURCE / "package_dashboard.py"), "--output", str(ROOT / "index.html")], check=True)
shutil.copyfile(ROOT / "index.html", ROOT / "wiki-activity-dashboard.html")
print("Build complete: index.html (also copied to wiki-activity-dashboard.html)")
