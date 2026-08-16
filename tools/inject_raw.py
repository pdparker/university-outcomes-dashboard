#!/usr/bin/env python3
"""Replace the `const RAW = {...};` line in index.html with a freshly built blob.

Usage: python3 tools/inject_raw.py raw.json index.html
"""
import json, sys

raw_path, html_path = sys.argv[1], sys.argv[2]
raw = open(raw_path).read().strip()
json.loads(raw)  # fail loudly rather than write a broken dashboard

lines = open(html_path).read().split("\n")
hits = [i for i, l in enumerate(lines) if l.lstrip().startswith("const RAW = ")]
if len(hits) != 1:
    sys.exit(f"expected exactly one `const RAW =` line, found {len(hits)}")
i = hits[0]
indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
before = len(lines[i])
lines[i] = f"{indent}const RAW = {raw};"
open(html_path, "w").write("\n".join(lines))
print(f"line {i + 1}: {before} -> {len(lines[i])} bytes")
