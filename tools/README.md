# Refreshing the data

The dashboard embeds its entire dataset in `index.html` as a single `const RAW = {...};`
line, so a refresh means re-scraping ComparED and rewriting that one line.

```bash
python3 tools/fetch_compared.py compared.db     # scrape the API into SQLite
python3 tools/build_raw.py compared.db raw.json # shape it into the dashboard's blob
python3 tools/inject_raw.py raw.json index.html # swap it into the page
```

Then open `index.html` and check the KPI row, the peer ranking chart, the UG/PG
toggle and a subject-area filter before committing.

## Where the data comes from

ComparED is an Angular SPA; the page HTML is an empty shell and every number
arrives from an undocumented JSON API at `api.compared.edu.au`:

| Endpoint | What it returns |
|---|---|
| `/institutions` | every provider, with headline highlights |
| `/institution/<alias>` | one provider in full, including the study areas it offers |
| `/study-areas` | the 21 study areas |
| `/study-area/<alias>` | national figures for one study area |

`fetch_compared.py` caches every response under `apicache/` — delete that
directory to force a genuinely fresh pull.

## Two traps

**Suppression is encoded as negative numbers, not nulls.** The API returns
`-1` where a cohort was too small to publish (`size` is non-zero but below the
threshold) and `-2` where no data was collected at all (`size` is 0). Left
alone these render as real scores and quietly poison national averages and
rankings. `fetch_compared.py` converts both to `NULL` on the way in.

**`skills-scale` and `teaching-scale` are currently empty for every
institution.** They are `-2` across the board, so the two metrics show as
blanks. That is the source's state, not a scrape failure.

## Survey vintages

GOS and SES are released on different cycles, so the metric families can sit a
year apart. As of the August 2026 refresh: Graduate Employment and Graduate
Satisfaction are the **2025 GOS**; Student Experience is the **2024 SES**.
Check which collection is live before assuming a change is real — and note the
2025 GOS redefined the labour force to match ABS definitions, which shifts the
employment metrics independently of any actual change in outcomes.
