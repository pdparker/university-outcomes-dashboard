#!/usr/bin/env python3
"""Build the RAW blob the dashboard embeds, from a compared.db."""
import json, sqlite3, sys

db = sys.argv[1]
con = sqlite3.connect(db)
con.row_factory = sqlite3.Row


def nz(v):
    """API suppression sentinels (-1 too-few-responses, -2 no-data) -> None."""
    if v is None:
        return None
    return None if v < 0 else v


universities = [dict(alias=r["alias"], title=r["title"], location=r["location"])
                for r in con.execute(
    "select alias,title,location from institutions where type='University' order by title")]
unis = {u["alias"] for u in universities}

study_areas = [dict(alias=r["alias"], title=r["title"])
               for r in con.execute("select alias,title from study_areas order by title")]

highlights, metrics_meta, seen = [], [], set()
for r in con.execute(
        "select h.* from institution_highlights h join institutions i on i.alias=h.institution_alias "
        "where i.type='University' order by h.id"):
    if r["metric_alias"] not in seen:
        seen.add(r["metric_alias"])
        metrics_meta.append(dict(alias=r["metric_alias"], title=r["metric_title"],
                                 group=r["metric_group"]))
    highlights.append({
        "ia": r["institution_alias"], "sl": r["study_level"], "ma": r["metric_alias"],
        "s": nz(r["score"]),
        "cl": nz(r["confidence_lower"]), "cu": nz(r["confidence_upper"]),
        "n": nz(r["national_avg_score"]),
        "nl": nz(r["national_avg_confidence_lower"]), "nu": nz(r["national_avg_confidence_upper"]),
        "ab": r["above_national_average"],
    })

inst_areas = {}
for r in con.execute("select institution_alias,study_area_alias from institution_study_area "
                     "order by institution_alias,study_area_alias"):
    if r["institution_alias"] in unis:
        inst_areas.setdefault(r["institution_alias"], []).append(r["study_area_alias"])

natl_avgs = {}
for r in con.execute(
        "select metric_alias,study_level,national_avg_score,national_avg_confidence_lower,"
        "national_avg_confidence_upper from institution_highlights "
        "where national_avg_score is not null and national_avg_score >= 0 group by metric_alias,study_level"):
    natl_avgs.setdefault(r["metric_alias"], {})[r["study_level"]] = {
        "score": r["national_avg_score"],
        "cl": r["national_avg_confidence_lower"],
        "cu": r["national_avg_confidence_upper"]}
for m in metrics_meta:
    natl_avgs.setdefault(m["alias"], {})

sa_highlights = [{
    "saa": r["study_area_alias"], "sl": r["study_level"], "ma": r["metric_alias"],
    "s": nz(r["score"]),
    "cl": nz(r["confidence_lower"]), "cu": nz(r["confidence_upper"]),
} for r in con.execute("select * from study_area_highlights order by study_area_alias,study_level,id")]

raw = {"universities": universities, "study_areas": study_areas, "highlights": highlights,
       "inst_areas": inst_areas, "natl_avgs": natl_avgs, "metrics_meta": metrics_meta,
       "sa_highlights": sa_highlights}
json.dump(raw, open(sys.argv[2], "w"), separators=(",", ":"))
print({k: len(v) for k, v in raw.items()})
