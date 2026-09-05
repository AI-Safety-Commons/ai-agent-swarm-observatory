#!/usr/bin/env python3
"""Package the dashboard fragment as a standalone, offline HTML document."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
DEFAULT_CSS = HERE / "dashboard.css"
D3_TAG = '<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>'


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.current_script = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        assert tag != "iframe", "Standalone document must not contain an iframe"
        assert "src" not in attrs, f"Unexpected external resource: {tag}"
        assert tag != "link", "Styles must be embedded"
        if tag == "script":
            self.current_script = [attrs, ""]

    def handle_data(self, data):
        if self.current_script is not None:
            self.current_script[1] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.scripts.append(self.current_script)
            self.current_script = None


def package(css_path, output):
    fragment = (HERE / "wiki-activity.html").read_text()
    css = css_path.read_text()
    d3 = (HERE / "d3-7.9.0.min.js").read_text()
    assert d3.startswith("// https://d3js.org v7.9.0 Copyright"), "Unexpected D3 bundle"
    assert fragment.count(D3_TAG) == 1, "Expected exactly one pinned D3 reference"
    assert not re.search(r"@import|url\(\s*['\"]?https?://", css), "Remote CSS resource"
    assert not re.search(r"\bfetch\s*\(|XMLHttpRequest|postMessage|window\.openai", fragment), "Host/network dependency"
    data_pattern = r'<script type="application/json" id="wa-data">(.*?)</script>'
    original_data = re.search(data_pattern, fragment, re.S).group(1)
    json.loads(original_data)
    fragment = fragment.replace(D3_TAG, '<script id="vendored-d3">\n' + d3 + '\n</script>')
    document = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Explore a curated wiki activity dataset: daily saves, deletions, user labels, and returning pages across four wikis.">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="website">
<meta property="og:title" content="Wiki Observatory — Every edit leaves a trace">
<meta property="og:description" content="An interactive view of wiki saves, deletions, contributors, and returning pages. May–July 2026.">
<title>Wiki Observatory — Every edit leaves a trace</title>
<style>
''' + css + '''
html > body { width: auto; margin: 0; padding: 0; }
</style>
</head>
<body>
''' + fragment + '\n</body>\n</html>\n'
    assert re.search(data_pattern, document, re.S).group(1) == original_data
    parsed = Document()
    parsed.feed(document)
    checked = 0
    with tempfile.TemporaryDirectory(prefix="wiki-dashboard-check-") as tmp:
        for attrs, script in parsed.scripts:
            if attrs.get("type") == "application/json":
                json.loads(script)
                continue
            path = Path(tmp) / f"script-{checked}.js"
            path.write_text(script)
            subprocess.run(["node", "--check", str(path)], check=True)
            checked += 1
    output.write_text(document)
    print(f"Created {output} ({output.stat().st_size:,} bytes)")
    print(f"Verified: data unchanged, {checked} JavaScript scripts parse, no external resources or host API dependency.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--css", type=Path, default=DEFAULT_CSS)
    parser.add_argument("--output", type=Path, default=HERE.parent / "wiki-activity-dashboard.html")
    args = parser.parse_args()
    package(args.css, args.output)
