# Swarm Observatory

**[Open the live dashboard](https://minsik-ai.github.io/ai-agent-swarm-observatory/)**

A static, interactive dashboard of **AI agent swarm activity** across four public wikis, covering May–July 2026. It includes daily activity, recorded user labels, page rankings, derived recreation relationships, administrator responses, and a revision sample viewer.

The swarm framing reflects page-history evidence of answer relays, task-clock coordination, and instructions shared between agents. It does not establish a single controller, provider, or verified number of agents; recorded labels may be reused.

## Precomputed activity summaries

The UI includes one paragraph for each of the top 20 **named** labels by saved revisions over the full export. The blank-label bucket is excluded. Select a label in **Precomputed activity summaries**, or click a linked label in the user table. Supporting-revision buttons open the exact revision in the sample viewer, including records beyond its first page of results.

Summaries were regenerated with `gpt-5.6-sol` at low reasoning effort as **overall per-user-label activity portraits**. They combine complete exported page-name inventories and per-label counts with page-reference patterns, shared-editor context, timing, and sampled revision changes. Task/cohort names, numbered continuations, and answer/status names are evaluated as possible communication addresses or signals—not just revision containers. Names alone do not establish that another agent read a message, replied, shared control, or succeeded in an evaluation; dates inside names need not be edit dates.

Inserted/replaced diff text was reviewed to avoid attributing inherited content to a saving label. Each summary has three source-validated revision references. Body evidence is sampled rather than exhaustive, and summaries do not update when chart filters change. Linked public samples are capped at 1,200 characters, so some supporting changes can occur beyond the displayed excerpt.

Reviewed paragraphs and provenance are committed in `visualizations/user-summaries.json`. Normal builds embed these cached results and **never invoke a model**; visitors incur no inference calls. The build checks dataset fingerprints, the top-20 ranking, counts, and all 60 evidence references before publication. `visualizations/build_summaries.py` is an optional packaging step requiring locally held source logs and reviewed drafts in `analysis/summary-page-review/` (or `--drafts-dir`); it does not generate text itself. Research drafts are excluded from Git.

## Open or publish

Open `index.html` in a browser. The release is self-contained: data, styles, and D3 are embedded, so it works offline without a server, accounts, analytics, or external requests.

The **Revision samples** panel opens all 14,591 saved revisions with independent date, user-label, wiki, and wiki-page filters. It shows ten records at a time, newest first. Expand a record to read up to 1,200 characters of its text; longer revisions are explicitly marked as truncated. Suggested full names match exactly; partial names use a case-insensitive search. These are saved revisions, not deletion/probe event samples.

Samples are bundled as gzip/base64 data and decompressed automatically after the dashboard's first paint using the browser's `DecompressionStream` API. No load button is needed; a retry button appears only if loading fails. A current Chrome, Firefox, Edge, or Safari is required for the viewer. No sample data is requested from a server. The self-contained release is approximately 2.5 MB.

To publish, upload **only `index.html`** to your static web host. No deployment or remote repository is created by this project. Do not upload the whole working directory, which may contain ignored source logs.

## Publish with GitHub Pages

The project already includes a built `index.html` and `.nojekyll` file. GitHub does not need to run Python or install dependencies to serve it.

1. Open Terminal in this repository and run `gh auth login`. Choose GitHub.com, HTTPS, and browser authentication. GitHub CLI is required for these commands.
2. Create and push a public repository:

   ```sh
   gh repo create ai-agent-swarm-observatory --public --source=. --remote=origin --push
   gh repo view --web
   ```

3. In the repository, open **Settings → Pages**. Under **Build and deployment**, set **Source** to **Deploy from a branch**, select **main** and **/(root)**, then **Save**.
4. Wait for the Pages deployment to complete. **Settings → Pages → Visit site** shows the URL, normally `https://YOUR_USERNAME.github.io/ai-agent-swarm-observatory/`. Publishing can take up to ten minutes.
5. For later changes, run `python3 build.py`, commit the updated source and `index.html`, then `git push`. Pages republishes changes pushed to the configured branch.

The public repository includes the committed source and aggregate data. Original logs and QA captures are excluded by `.gitignore`.

References: [Push a local repository](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github), [configure the Pages source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site), [create and view a Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

## Build

Requires Python 3.9+ and Node.js (used only to check JavaScript syntax). No package installation is required.

```sh
python3 build.py
```

This validates aggregate totals, produces `index.html`, and refreshes the local `wiki-activity-dashboard.html` compatibility copy. Edit `visualizations/wiki-activity.template.html` for markup/chart behavior and `visualizations/dashboard.css` for the theme. The build does not require the original logs or any Codex plugins.

## Validate

```sh
python3 visualizations/verify_charts.py
python3 visualizations/test_samples.py
```

The browser checks require Google Chrome; set `CHROME_BIN` if it is not in the standard macOS location. They verify counts, filters, page/user colors, Top 100 controls, pagination, attribution, and layout across desktop/mobile and light/dark cases. Generated captures and reports are ignored by Git.

## Data and interpretation

The supplied `full-wiki-logs` export was generated on September 3, 2026. Its stored-revision cut uses write dates from May 1 onward. Exported events shown by the dashboard span May 17–July 14; different populations have different end dates.

- 14,591 held revisions across 4,579 stored pages and four wikis.
- 5,217 administrator deletion events, 101 script probes, and four recovery records without held revisions.
- 68 derived first-recreation relations across 50 pages.

These populations overlap. Their sum is not a count of unique incidents. User labels are recorded names rather than verified identities. Some timestamps and recreation links use fallback records. Missing records do not prove activity stopped.

The committed aggregate data retains dates, wiki names, recorded user labels, page identifiers, counts, and population metadata. The separate compressed sample bundle additionally includes bounded revision-body excerpts, revision sequence numbers, timing grades, and truncation/redaction flags. The summary bundle contains the reviewed paragraphs and logical revision identifiers for evidence navigation. It excludes raw diffs, IP metadata fields, request-log URLs, and raw source-file locations. Source links within excerpts remain plain text, with selected credential values redacted.

Before truncation, the sample exporter decodes the source bytes and replaces email addresses, valid IP addresses, and selected credential/token patterns in revision text. Pattern matching is not comprehensive anonymization: labels, page identifiers, and the remaining excerpt text are intentionally retained. Short revisions may be shown in full.

`visualizations/build_data.py` can regenerate the aggregate JSON when the original, untracked `full-wiki-logs/` directory is present. The curated aggregate data is committed so the public build remains reproducible without those logs.

To regenerate samples from the same source, run `python3 visualizations/build_samples.py` after regenerating chart data, then `python3 build.py`. The build verifies the sample checksum and dictionary fingerprint to prevent mislabeling excerpts with stale indices. Normal builds use the committed sample bundle and do not need source logs.

## Cite As
```
@misc{swarm_observatory,
  author = {Minsik Oh},
  title = {AI Agent Swarm Observatory},
  year = {2026},
  url = {https://minsik-ai.github.io/ai-agent-swarm-observatory/},
}
```
