# Australian University Outcomes Dashboard

An interactive, self-contained dashboard for comparing Australian university outcomes across student experience, graduate satisfaction, and graduate employment metrics.

**Live demo:** https://pdparker.github.io/university-outcomes-dashboard/

## Features

- **My Institution** focus mode — select any of 49 Australian universities and the whole dashboard re-centres around it
- **UG / PG toggle** — switch between undergraduate and postgraduate data
- **Peer Ranking chart** — all universities sorted by any metric, with 95% confidence interval error bars and a national average reference line
- **Full Metric Profile** — all 13 metrics across 3 groups (Student Experience, Graduate Satisfaction, Graduate Employment) compared against national averages
- **Subject Area filter** — filter rankings to universities offering a specific field of study, benchmarked against field-specific national averages
- **Study Areas** — visual map of which of 21 subject areas the selected institution offers
- **Sortable Rankings Table** — all universities with scores, confidence intervals, and vs-average indicators

## Data

Data sourced from [compared.edu.au](https://www.compared.edu.au/) (the public face of the Australian Government's QILT surveys). Covers 49 Australian universities across 13 outcome metrics and 21 study areas at both undergraduate and postgraduate levels.

**Last refreshed:** 14 November 2026.

The two survey families run on different release cycles, so the dashboard's metrics are not all from the same collection year:

| Metric group | Survey | Collection |
|---|---|---|
| Graduate Employment, Graduate Satisfaction | Graduate Outcomes Survey (GOS) | 2025 |
| Student Experience | Student Experience Survey (SES) | 2025 |

Two caveats worth knowing:

- The 2025 GOS changed how the labour force is defined, aligning it with ABS definitions. Employment metrics are therefore **not strictly comparable** with earlier years.
- The University of Adelaide and the University of South Australia have merged into **Adelaide University**, which now reports as a single institution. The two predecessor entries are gone, so year-on-year comparisons for South Australia break at this point.

Scores are suppressed by the source where a cohort is too small to publish; those appear as blanks rather than zeros.

## Usage

Open `index.html` in any modern browser — no server or internet connection required. All data is embedded directly in the file.

## Deployment (GitHub Pages)

This file is deployed via GitHub Pages. Any push to the `main` branch automatically updates the live site.
