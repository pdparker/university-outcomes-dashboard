#!/usr/bin/env python3
"""Fetch the full ComparED dataset from api.compared.edu.au into a SQLite DB.

Endpoints used (discovered from the Angular SPA's XHR calls):
  GET /institutions              -> list of all providers (with highlights)
  GET /institution/<alias>       -> provider detail incl. studyAreas offered
  GET /study-areas               -> list of the 21 study areas
  GET /study-area/<alias>        -> national study-area detail incl. highlights
"""
import json, os, sqlite3, sys, time, urllib.request

API = "https://api.compared.edu.au"
OUT = sys.argv[1] if len(sys.argv) > 1 else "compared-new.db"
CACHE = "apicache"
os.makedirs(CACHE, exist_ok=True)


def get(path):
    fn = os.path.join(CACHE, path.strip("/").replace("/", "_") + ".json")
    if os.path.exists(fn):
        return json.load(open(fn))
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Origin": "https://www.compared.edu.au",
        "Referer": "https://www.compared.edu.au/",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.load(r)
            json.dump(data, open(fn, "w"))
            time.sleep(0.3)
            return data
        except Exception as e:
            if attempt == 3:
                raise
            print(f"  retry {path}: {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))


SCHEMA = """
DROP TABLE IF EXISTS institutions;
DROP TABLE IF EXISTS institution_metrics;
DROP TABLE IF EXISTS institution_highlights;
DROP TABLE IF EXISTS study_areas;
DROP TABLE IF EXISTS study_area_metrics;
DROP TABLE IF EXISTS study_area_highlights;
DROP TABLE IF EXISTS institution_study_area;
CREATE TABLE institutions(alias TEXT PRIMARY KEY,title TEXT,type TEXT,location TEXT,website_url TEXT);
CREATE TABLE institution_metrics(id INTEGER PRIMARY KEY,institution_alias TEXT,study_level TEXT,ses_count INTEGER,gos_count INTEGER,goe_count INTEGER);
CREATE TABLE institution_highlights(id INTEGER PRIMARY KEY,institution_alias TEXT,study_level TEXT,metric_alias TEXT,metric_title TEXT,metric_group TEXT,score REAL,confidence_lower REAL,confidence_upper REAL,size INTEGER,national_avg_score REAL,national_avg_confidence_lower REAL,national_avg_confidence_upper REAL,national_avg_size INTEGER,above_national_average INTEGER);
CREATE TABLE study_areas(alias TEXT PRIMARY KEY,title TEXT,description TEXT);
CREATE TABLE study_area_metrics(id INTEGER PRIMARY KEY,study_area_alias TEXT,study_level TEXT,ses_count INTEGER,gos_count INTEGER,goe_count INTEGER);
CREATE TABLE study_area_highlights(id INTEGER PRIMARY KEY,study_area_alias TEXT,study_level TEXT,metric_alias TEXT,metric_title TEXT,metric_group TEXT,score REAL,confidence_lower REAL,confidence_upper REAL,size INTEGER,national_avg_score REAL,national_avg_confidence_lower REAL,national_avg_confidence_upper REAL,national_avg_size INTEGER,above_national_average INTEGER);
CREATE TABLE institution_study_area(institution_alias TEXT,study_area_alias TEXT,PRIMARY KEY(institution_alias,study_area_alias));
"""

LEVELS = [("undergraduate", "UG"), ("postgraduate", "PG")]


def hl_rows(block, key, alias, lvl):
    for h in (block.get("highlights") or []):
        yield (alias, lvl, h["alias"], h["title"], h["group"], h.get("score"),
               h.get("confidenceLevelLower"), h.get("confidenceLevelUpper"), h.get("size"),
               h.get("nationalAverageScore"), h.get("nationalAverageConfidenceLevelLower"),
               h.get("nationalAverageConfidenceLevelUpper"), h.get("nationalAverageSize"),
               1 if h.get("aboveNationalAverage") else 0)


con = sqlite3.connect(OUT)
con.executescript(SCHEMA)

print("→ /institutions")
insts = get("/institutions")
print(f"  {len(insts)} providers")

for i, inst in enumerate(insts, 1):
    alias = inst["alias"]
    print(f"  [{i}/{len(insts)}] {alias}")
    detail = get(f"/institution/{alias}")
    con.execute("INSERT OR REPLACE INTO institutions VALUES(?,?,?,?,?)",
                (alias, inst["title"], inst["type"],
                 ",".join(inst.get("location") or []), inst.get("websiteUrl")))
    for key, lvl in LEVELS:
        block = detail.get(key) or {}
        con.execute("INSERT INTO institution_metrics(institution_alias,study_level,ses_count,gos_count,goe_count) VALUES(?,?,?,?,?)",
                    (alias, lvl, block.get("studentExperienceCount"),
                     block.get("graduateSatisfactionCount"), block.get("graduateEmploymentCount")))
        con.executemany(
            "INSERT INTO institution_highlights(institution_alias,study_level,metric_alias,metric_title,metric_group,score,confidence_lower,confidence_upper,size,national_avg_score,national_avg_confidence_lower,national_avg_confidence_upper,national_avg_size,above_national_average) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            list(hl_rows(block, key, alias, lvl)))
    for sa in (detail.get("studyAreas") or []):
        con.execute("INSERT OR IGNORE INTO institution_study_area VALUES(?,?)", (alias, sa["alias"]))

print("→ /study-areas")
sas = get("/study-areas")
for sa in sas:
    alias = sa["alias"]
    print(f"  {alias}")
    detail = get(f"/study-area/{alias}")
    con.execute("INSERT OR REPLACE INTO study_areas VALUES(?,?,?)",
                (alias, sa["title"], sa.get("description")))
    for key, lvl in LEVELS:
        block = detail.get(key) or {}
        con.execute("INSERT INTO study_area_metrics(study_area_alias,study_level,ses_count,gos_count,goe_count) VALUES(?,?,?,?,?)",
                    (alias, lvl, block.get("studentExperienceCount"),
                     block.get("graduateSatisfactionCount"), block.get("graduateEmploymentCount")))
        con.executemany(
            "INSERT INTO study_area_highlights(study_area_alias,study_level,metric_alias,metric_title,metric_group,score,confidence_lower,confidence_upper,size,national_avg_score,national_avg_confidence_lower,national_avg_confidence_upper,national_avg_size,above_national_average) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            list(hl_rows(block, key, alias, lvl)))

# The API encodes suppression as negative sentinels: -1 = sample below the
# publication threshold, -2 = no data collected. Store both as NULL.
for tbl in ("institution_highlights", "study_area_highlights"):
    for col in ("score", "confidence_lower", "confidence_upper", "national_avg_score",
                "national_avg_confidence_lower", "national_avg_confidence_upper"):
        con.execute(f"UPDATE {tbl} SET {col}=NULL WHERE {col} < 0")

con.commit()
for t in ("institutions", "institution_highlights", "institution_study_area",
          "study_areas", "study_area_highlights"):
    print(t, con.execute(f"select count(*) from {t}").fetchone()[0])
con.close()
print("wrote", OUT)
