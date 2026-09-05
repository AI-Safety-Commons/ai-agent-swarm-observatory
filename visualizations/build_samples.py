"""Export bounded, redacted revision excerpts, compressed for offline browsing."""
import base64
from collections import Counter
import gzip
import hashlib
import ipaddress
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
LIMIT = 1200
FIELDS = ['time', 'wiki', 'label', 'page', 'seq', 'excerpt', 'truncated', 'redactions', 'timeGrade']
EMAIL = re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b')
IP = re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])|(?<!\w)(?:[a-fA-F0-9]{0,4}:){2,7}[a-fA-F0-9]{0,4}(?!\w)')
CREDENTIAL = re.compile(r'''(?ix)(\b(?:api[-_]?key|access[-_]?token|refresh[-_]?token|auth[-_]?token|password|passwd|secret|resourcekey)\b["']?\s*(?:=|:|%3d)\s*["']?)([^\s&<>"']+)''')
TOKEN = re.compile(r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b|(?i:Bearer)\s+[A-Za-z0-9._~+/-]{12,}')


def redact(text):
    count = 0
    text, n = EMAIL.subn('[REDACTED_EMAIL]', text)
    count += n

    def replace_ip(match):
        nonlocal count
        try:
            ipaddress.ip_address(match.group())
        except ValueError:
            return match.group()
        count += 1
        return '[REDACTED_IP]'

    text = IP.sub(replace_ip, text)
    text, n = CREDENTIAL.subn(lambda m: m.group(1) + '[REDACTED]', text)
    count += n
    text, n = TOKEN.subn('[REDACTED_TOKEN]', text)
    return text, count + n


def main():
    chart = json.loads((HERE / 'chart-data.json').read_text())
    wiki_ids, label_ids, page_ids = [{v: i for i, v in enumerate(chart[k])} for k in ['wikis', 'labels', 'pages']]
    rows, redacted_rows, truncated_rows = [], 0, 0
    with (HERE.parent / 'full-wiki-logs/revisions.jsonl').open(encoding='utf-8') as source:
        for line in source:
            r = json.loads(line)
            encoding = {'ascii': 'ascii', 'utf8': 'utf-8', 'latin1': 'latin-1'}[r['body_encoding']]
            original = r['body'].encode('latin-1').decode(encoding)
            text, replacements = redact(original)
            truncated = len(text) > LIMIT
            rows.append([r['time'], wiki_ids[r['wiki']], label_ids[r['label'] or '(blank label)'], page_ids[r['page_id']], r['seq'], text[:LIMIT], truncated, replacements, r['time_grade']])
            redacted_rows += bool(replacements)
            truncated_rows += truncated
    rows.sort(key=lambda r: (r[0], r[3], r[4]), reverse=True)
    assert len(rows) == len({(r[3], r[4]) for r in rows}) == 14591
    assert Counter(chart['wikis'][r[1]] for r in rows) == {'dse': 13403, 'probier': 1013, 'fractal': 169, 'dorfwiki': 6}
    payload = {'fields': FIELDS, 'rows': rows, 'count': len(rows), 'excerptLimit': LIMIT,
               'minDate': min(r[0][:10] for r in rows), 'maxDate': max(r[0][:10] for r in rows),
               'redactedRevisions': redacted_rows, 'truncatedRevisions': truncated_rows,
               'dictionarySha256': hashlib.sha256(json.dumps([chart[k] for k in ['wikis', 'labels', 'pages']], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()}
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()
    archive = {'encoding': 'gzip-base64', 'sha256': hashlib.sha256(raw).hexdigest(), 'count': len(rows),
               'data': base64.b64encode(gzip.compress(raw, mtime=0)).decode('ascii')}
    (HERE / 'sample-data.json').write_text(json.dumps(archive, separators=(',', ':')) + '\n')
    print(json.dumps({'revisions': len(rows), 'rawBytes': len(raw), 'packedBytes': (HERE / 'sample-data.json').stat().st_size, 'redactedRevisions': redacted_rows, 'truncatedRevisions': truncated_rows}))


if __name__ == '__main__':
    main()
