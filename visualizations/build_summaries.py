"""Package reviewed model output; never invokes a model during a site build."""
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    chart_bytes = (HERE / 'chart-data.json').read_bytes()
    chart = json.loads(chart_bytes)
    counts = Counter()
    page_sets = {}
    for r in chart['rows']:
        if r[2] == 0 and chart['labels'][r[3]] != '(blank label)':
            label = chart['labels'][r[3]]
            counts[label] += r[5]
            page_sets.setdefault(label, set()).add(r[4])
    top = sorted(counts, key=lambda label: (-counts[label], label))[:20]
    drafts = json.loads((ROOT / 'analysis/summary-pilot/top-10-user-summaries.json').read_text())['summaries']
    packets = json.loads((ROOT / 'analysis/summary-pilot/packets.json').read_text())
    for n in (1, 2):
        drafts += json.loads((ROOT / f'analysis/summary-expansion/summaries-{n}.json').read_text())
        packets += json.loads((ROOT / f'analysis/summary-expansion/packets-{n}.json').read_text())
    assert [d['label'] for d in drafts] == top
    by_packet = {p['label']: p for p in packets}
    revisions = [json.loads(line) for line in (ROOT / 'full-wiki-logs/revisions.jsonl').open()]
    public = []
    for rank, draft in enumerate(drafts, 1):
        label = draft['label']
        packet = by_packet[label]
        assert packet['saved_revisions'] == counts[label]
        evidence = []
        for e in draft['evidence']:
            row = revisions[e['source_line'] - 1]
            assert row['rev_id'] == e['revision'] and row['label'] == label
            evidence.append({'revision': row['rev_id'], 'page': row['page_id'], 'seq': row['seq'], 'time': row['time'], 'reason': e['reason']})
        public.append({'rank': rank, 'label': label, 'saved_revisions': counts[label], 'page_count': len(page_sets[label]),
                       'paragraph': draft['paragraph'], 'evidence': evidence,
                       'period': {'from': packet['first_time'], 'to': packet['last_time']},
                       'evidenceHash': hashlib.sha256(json.dumps(packet, sort_keys=True, ensure_ascii=False).encode()).hexdigest()})
    result = {'model': 'gpt-5.6-sol', 'reasoningEffort': 'low', 'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'chartSha256': hashlib.sha256(chart_bytes).hexdigest(),
              'scope': 'Top 20 nonblank labels by saved revisions across the full exported snapshot. Summaries do not change with chart filters.',
              'method': 'Precomputed from complete label statistics and sampled revision text, checked against inserted/replaced diff text. Labels are not verified individual agents. Execution and success claims are not independently verified.',
              'summaries': public}
    (HERE / 'user-summaries.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print('Packaged 20 reviewed summaries and 60 source-validated revision references.')


if __name__ == '__main__':
    main()
