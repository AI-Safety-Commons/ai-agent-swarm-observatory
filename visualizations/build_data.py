"""Build compact chart aggregates without exporting bodies or network identifiers."""

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "full-wiki-logs"
TYPES = {"save": 0, "delete": 1, "probe": 2, "revert": 3}


def records(name):
    with (SOURCE / name).open(encoding="utf-8") as source:
        for line in source:
            yield json.loads(line)


def label(value):
    if value is None:
        return "(unattributed)"
    return value if value != "" else "(blank label)"


def main():
    revision_labels = {r["rev_id"]: label(r.get("label")) for r in records("revisions.jsonl")}
    events = list(records("events.jsonl"))
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    assert manifest["population_counts"]["probe"]["population_id"] == "dse_script_probe_requests"
    dates = sorted({e["time"][:10] for e in events})
    wikis = sorted({e.get("wiki", "dse") for e in events})
    labels = sorted(set(revision_labels.values()) | {label(e.get("actor_label")) for e in events} | {"(blank label)", "(unattributed)"})
    pages = sorted({f'{e["wiki"]}/{e["page"]}' for e in events if "page" in e})
    date_index, wiki_index, label_index, page_index = [{v: i for i, v in enumerate(values)} for values in (dates, wikis, labels, pages)]
    rows, recreations, counts, grades = Counter(), Counter(), Counter(), Counter()
    revision_refs = set()
    for event in events:
        kind = event["event_type"]
        actor = revision_labels[event["revision_ref"]] if kind == "save" else label(event.get("actor_label"))
        if kind == "save":
            assert event["revision_ref"] not in revision_refs
            revision_refs.add(event["revision_ref"])
        wiki = event.get("wiki", "dse")
        assert "wiki" in event or kind == "probe"
        page = page_index[f'{wiki}/{event["page"]}'] if "page" in event else -1
        date, wiki_id = date_index[event["time"][:10]], wiki_index[wiki]
        rows[date, wiki_id, TYPES[kind], label_index[actor], page] += 1
        counts[kind] += 1
        grades[f'{kind}:{event["time_grade"]}'] += 1
        if event.get("relation_type") == "first_recreation_of":
            assert kind in ("save", "revert")
            related = event["related_event_id"]
            edges = related if isinstance(related, list) else [related]
            assert all(edges)
            recreations[date, wiki_id, page] += len(edges)
    assert counts == {"save": 14591, "delete": 5217, "probe": 101, "revert": 4}, counts
    assert sum(rows.values()) == 19913
    assert revision_refs == set(revision_labels)
    assert sum(recreations.values()) == 68
    assert len({key[2] for key in recreations}) == 50
    output = {
        "dates": dates, "wikis": wikis, "labels": labels, "pages": pages,
        "rows": [[*key, count] for key, count in sorted(rows.items())],
        "recreations": [[*key, count] for key, count in sorted(recreations.items())],
        "meta": {
            "typeNames": ["Stored saves", "Admin deletions", "Script probes", "Recovery records"],
            "typeCounts": [counts[k] for k in TYPES],
            "physicalEventRows": len(events),
            "recreationEdges": 68, "recreationPages": 50,
            "heldRevisionPages": manifest["counts"]["pages"]["value"],
            "minTimeUTC": min(e["time"] for e in events),
            "maxTimeUTC": max(e["time"] for e in events),
            "timeZone": "UTC",
            "timeGrades": dict(sorted(grades.items())),
            "source": "full-wiki-logs/events.jsonl joined to revisions.jsonl by revision_ref",
            "exportGeneratedAt": manifest["generated_at"],
            "caveats": [
                "Curated populations have different coverage. Saves, deletions, probes and recovery records must not be added as unique incidents; 19,913 is only the physical event-row count.",
                "Saves represent held revisions with write_date >= 2026-05-01. Administrator deletions and script probes are DSE-specific populations, not complete cross-wiki traffic.",
                "User charts group verbatim preference or actor labels, not authenticated people. Reused labels may represent many executions; blank labels and missing attribution remain separate.",
                "Probe rows omit wiki; DSE attribution follows the manifest population dse_script_probe_requests. Probes have no published page or actor label, and none records observed success.",
                "The four event_type=revert rows are first-recreation recovery records without held revisions; they do not establish native wiki reverts.",
                "Recreation totals count derived first_recreation_of edges, not unique incidents: 68 edges across 50 pages. Multiple edges may reference one revision.",
                "Timeline uses each event's exported time in UTC, including fallback clocks. Saves: 14,482 reqlog, 103 rclog and 6 write_date grades; deletions: 5,216 reqlog and 1 rclog. Recreation edges inherit their linked event dates.",
                "Different population end dates prevent interpreting a late decline in saves as proof that activity stopped."
            ]
        }
    }
    target = HERE / "chart-data.json"
    target.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"file": str(target), "bytes": target.stat().st_size, "aggregateRows": len(rows), "counts": counts, "recreationEdges": sum(recreations.values()), "recreationPages": 50, "dates": [dates[0], dates[-1]]}))


if __name__ == "__main__":
    main()
