# Swarm Observatory

A static, interactive dashboard of **AI agent swarm activity** across four public wikis, covering May–July 2026. It includes daily activity, recorded user labels, page rankings, derived recreation relationships, and administrator responses.

The swarm framing reflects page-history evidence of answer relays, task-clock coordination, and instructions shared between agents. It does not establish a single controller, provider, or verified number of agents; recorded labels may be reused.

## Open or publish

Open `index.html` in a browser. The release is self-contained: data, styles, and D3 are embedded, so it works offline without a server, accounts, analytics, or external requests.

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
