# Wiki Observatory

A static, interactive dashboard for a curated wiki activity export covering May–July 2026. It includes daily activity, recorded user labels, page rankings, and derived recreation relationships.

## Open or publish

Open `index.html` in a browser. The release is self-contained: data, styles, and D3 are embedded, so it works offline without a server, accounts, analytics, or external requests.

To publish, upload **only `index.html`** to your static web host. No deployment or remote repository is created by this project. Do not upload the whole working directory, which may contain ignored source logs.

## Build

Requires Python 3.9+ and Node.js (used only to check JavaScript syntax). No package installation is required.

```sh
python3 build.py
```

This validates aggregate totals, produces `index.html`, and refreshes the local `wiki-activity-dashboard.html` compatibility copy. Edit `visualizations/wiki-activity.template.html` for markup/chart behavior and `visualizations/dashboard.css` for the theme. The build does not require the original logs or any Codex plugins.

## Validate

```sh
python3 visualizations/verify_charts.py
```

The browser checks require Google Chrome; set `CHROME_BIN` if it is not in the standard macOS location. They verify counts, filters, page/user colors, Top 100 controls, pagination, attribution, and layout across desktop/mobile and light/dark cases. Generated captures and reports are ignored by Git.

## Data and interpretation

The supplied `full-wiki-logs` export was generated on September 3, 2026. Its stored-revision cut uses write dates from May 1 onward. Exported events shown by the dashboard span May 17–July 14; different populations have different end dates.

- 14,591 held revisions across 4,579 stored pages and four wikis.
- 5,217 administrator deletion events, 101 script probes, and four recovery records without held revisions.
- 68 derived first-recreation relations across 50 pages.

These populations overlap. Their sum is not a count of unique incidents. User labels are recorded names rather than verified identities. Some timestamps and recreation links use fallback records. Missing records do not prove activity stopped.

The committed aggregate data retains dates, wiki names, recorded user labels, page identifiers, counts, and population metadata. It excludes revision bodies, diffs, IP fields, request URLs, and raw source references. Labels and page identifiers remain visible; this is not a fully anonymized dataset.

`visualizations/build_data.py` can regenerate the aggregate JSON when the original, untracked `full-wiki-logs/` directory is present. The curated aggregate data is committed so the public build remains reproducible without those logs.

## Third-party and data rights

D3 7.9.0 is vendored with its copyright notice and license in `visualizations/D3-LICENSE`. No upstream URL or redistribution license for the supplied dataset was included in its manifest; this repository does not grant additional rights to that source data. No project-wide license has been assigned.
