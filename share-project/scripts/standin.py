#!/usr/bin/env python3
# share-project/scripts/standin.py
# Purpose: write a stand-in for a data file: same file, sheet, table and column names, a few invented rows of matching types.
# Non-goals: never copies a value from a personal column, never prints an original value, never writes over the original.
"""Make a stand-in for a data file.

Usage: python3 standin.py <data-file> <stand-in-file> [--rows N] [--pack <pack-folder>] [--json]

With --pack, the stand-in (which must sit under <pack-folder>/project/) is recorded with its
fingerprint in <pack-folder>/STANDINS.json; check_pack.py accepts a data file only if it is
recorded there unchanged.

Supported: .csv, .tsv, .xlsx / .xlsm (read and written with the standard library) and SQLite
files (.db, .sqlite, .sqlite3). Anything else, or a file that cannot be read, exits 1 with
"left out" and the reason; the caller leaves that file out of the pack.

Invented values: text becomes "standin-<column>-<n>"; emails "standin-<n>@example.invalid";
phones "000-555-01nn"; dates stay inside the months the original covers; numbers keep their
kind (whole or decimal) and rough size. A short category column (few repeated labels such as
department names) keeps its labels so rules that depend on them still work, unless the column
name looks personal; the result lists every column whose labels were kept so the owner can see them.
Exit 0 = written; 1 = left out (reason printed); 2 = usage error."""

import csv
import json
import os
import random
import re
import sqlite3
import sys
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

PERSONAL_HINT = re.compile(
    r"name|customer|client|buyer|cobuyer|owner|contact|person|people|employee|staff|salesperson|sales_?rep|rep\b|"
    r"advisor|tech|manager|user|email|e-mail|phone|mobile|cell|fax|address|street|city|zip|postal|ssn|social|"
    r"dob|birth|licen[cs]e|vin|plate|account|card|iban|routing|pay|salary|wage|income|tax_?id|ip_?addr|note|comment",
    re.I)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$")
NUM = re.compile(r"^-?\d+(\.\d+)?$")
PERSON = re.compile(r"^[A-Z][a-z'\u00e0-\u00ff-]+( [A-Z][a-z'\u00e0-\u00ff-]+){1,3}$")
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
MAX_INPUT = 200 * 1024 * 1024


class LeftOut(Exception):
    pass


def profile(name, values):
    """Describe a column without keeping any of its values except short category labels."""
    vals = [v for v in values if v not in (None, "")]
    blanks = len(values) - len(vals)
    texts = [str(v) for v in vals]
    looks_like_names = (len(texts) >= 3 and sum(bool(PERSON.match(t)) for t in texts) >= 0.8 * len(texts)
                        and len(set(texts)) > 0.5 * len(texts))
    p = {"name": name, "blanks": blanks > 0, "personal": bool(PERSONAL_HINT.search(name or "")) or looks_like_names}
    if not texts:
        p["type"] = "text"
    elif all(isinstance(v, (int, float)) or NUM.match(t) for v, t in zip(vals, texts)):
        decimals = max((len(t.split(".")[1]) for t in texts if "." in t), default=0)
        mags = sorted(abs(float(t)) for t in texts)
        median = mags[len(mags) // 2]
        p.update(type="number", decimals=min(decimals, 2), size=10 ** max(0, len(str(int(median))) - 1), median=median)
    elif all(DATE.match(t) for t in texts):
        months = sorted({t[:7] for t in texts})
        p.update(type="date", months=months, time=any(len(t) > 10 for t in texts))
    elif all(re.match(r"^\d{4}-\d{2}$", t) for t in texts):
        p.update(type="month", months=sorted(set(texts)))
    else:
        p["type"] = "text"
        distinct = sorted(set(texts))
        if (not p["personal"] and len(distinct) <= 12 and len(texts) >= 2 * len(distinct)
                and all(len(t) <= 24 and "@" not in t and not re.search(r"\d{3}", t) for t in distinct)):
            p["labels"] = distinct
        elif any("@" in t for t in texts):
            p["email"] = True
        elif any(re.search(r"\d{3}[ .-]\d{3}[ .-]\d{4}", t) for t in texts):
            p["phone"] = True
    return p


def rank_numbers(profiles):
    """Keep only the order of same-size number columns (a price above its cost), then forget the medians."""
    by_size = {}
    for p in profiles:
        if p["type"] == "number":
            by_size.setdefault(p["size"], []).append(p)
    for group in by_size.values():
        for rank, p in enumerate(sorted(group, key=lambda q: -q["median"])):
            p["rank"] = rank
    for p in profiles:
        p.pop("median", None)
    return profiles


def invent_row(profiles, n, rng, rows):
    factor = rng.randint(20, 80) / 10
    return [invent(p, n, rng, rows, factor) for p in profiles]


def invent(p, n, rng, rows, factor=5.0):
    if p["blanks"] and n == rows - 1:
        return None
    col = re.sub(r"[^a-z0-9]+", "-", (p["name"] or "column").lower()).strip("-") or "column"
    if p["type"] == "number":
        v = p["size"] * factor * (1 - 0.08 * p.get("rank", 0)) + (rng.randint(0, 99) / 100 if p["decimals"] else 0)
        return round(v, p["decimals"]) if p["decimals"] else int(v)
    if p["type"] == "month":
        return p["months"][n % len(p["months"])]
    if p["type"] == "date":
        month = p["months"][n % len(p["months"])]
        d = f"{month}-{1 + (n * 7) % 27:02d}"
        return d + (" 09:00:00" if p.get("time") else "")
    if p.get("labels"):
        return p["labels"][n % len(p["labels"])]
    if p.get("email") or re.search(r"e-?mail", p["name"] or "", re.I):
        return f"standin-{n + 1}@example.invalid"
    if p.get("phone") or re.search(r"phone|mobile|cell|fax", p["name"] or "", re.I):
        return f"000-555-01{n + 10:02d}"
    return f"standin-{col}-{n + 1}"


# ---------- CSV / TSV ----------

def csv_standin(src, dst, rows, rng):
    delim = "\t" if src.lower().endswith(".tsv") else ","
    with open(src, newline="", encoding="utf-8-sig", errors="strict") as f:
        reader = csv.reader(f, delimiter=delim)
        try:
            header = next(reader)
        except StopIteration:
            raise LeftOut("empty file")
        body = [r for _, r in zip(range(5000), reader)]
    profiles = rank_numbers([profile(h, [r[i] if i < len(r) else "" for r in body]) for i, h in enumerate(header)])
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=delim)
        w.writerow(header)
        for n in range(rows):
            w.writerow(["" if v is None else v for v in invent_row(profiles, n, rng, rows)])
    return {"sheets": [{"name": os.path.basename(src), "columns": profiles}]}


# ---------- XLSX ----------

def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path):
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist()) > MAX_INPUT:
            raise LeftOut("workbook too large to read safely")
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{{{NS}}}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS}}}t")))
        sheets = []
        for sh in wb.find(f"{{{NS}}}sheets"):
            target = targets[sh.get(RID)]
            part = target.lstrip("/") if target.startswith("/") else "xl/" + target
            xml = ET.fromstring(z.read(part))
            grid = []
            for row in xml.iter(f"{{{NS}}}row"):
                cells = {}
                for c in row.findall(f"{{{NS}}}c"):
                    t, v = c.get("t"), c.find(f"{{{NS}}}v")
                    if t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(f"{{{NS}}}t"))
                    elif t == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif v is not None:
                        val = float(v.text) if t in (None, "n") and NUM.match(v.text or "") else v.text
                        if isinstance(val, float) and val.is_integer():
                            val = int(val)
                    else:
                        val = ""
                    cells[_col_index(c.get("r"))] = val
                width = max(cells) + 1 if cells else 0
                grid.append([cells.get(i, "") for i in range(width)])
            sheets.append((sh.get("name"), grid))
        return sheets


def write_xlsx(path, sheets):
    """sheets: [(name, header, rows)]. Inline strings and numbers only."""
    def col(n):
        s = ""
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s

    def sheet_xml(header, rows):
        out = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="{NS}"><sheetData>']
        for r, values in enumerate([header] + rows, start=1):
            cells = []
            for c, v in enumerate(values, start=1):
                if v is None or v == "":
                    continue
                ref = f"{col(c)}{r}"
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    cells.append(f'<c r="{ref}"><v>{v}</v></c>')
                else:
                    cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>')
            out.append(f'<row r="{r}">{"".join(cells)}</row>')
        return "".join(out) + "</sheetData></worksheet>"

    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    PR = "http://schemas.openxmlformats.org/package/2006/relationships"
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>']
    wbs, wbr = [], []
    for i, (name, _, _) in enumerate(sheets, start=1):
        ct.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        wbs.append(f'<sheet name="{escape(name, {chr(34): "&quot;"})}" sheetId="{i}" r:id="rId{i}"/>')
        wbr.append(f'<Relationship Id="rId{i}" Type="{R}/worksheet" Target="worksheets/sheet{i}.xml"/>')
    ct.append("</Types>")
    parts = {
        "[Content_Types].xml": "".join(ct),
        "_rels/.rels": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PR}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="{NS}" xmlns:r="{R}"><sheets>{"".join(wbs)}</sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PR}">{"".join(wbr)}</Relationships>',
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)), data)
        for i, (_, header, rows) in enumerate(sheets, start=1):
            z.writestr(zipfile.ZipInfo(f"xl/worksheets/sheet{i}.xml", (2026, 1, 1, 0, 0, 0)), sheet_xml(header, rows))


def xlsx_standin(src, dst, rows, rng):
    out, report = [], []
    for name, grid in read_xlsx(src):
        if not grid:
            out.append((name, [], []))
            report.append({"name": name, "columns": []})
            continue
        header = ["" if h is None else h for h in grid[0]]
        body = grid[1:5001]
        profiles = rank_numbers([profile(str(h), [r[i] if i < len(r) else "" for r in body]) for i, h in enumerate(header)])
        out.append((name, header, [invent_row(profiles, n, rng, rows) for n in range(rows)]))
        report.append({"name": name, "columns": profiles})
    write_xlsx(dst, out)
    return {"sheets": report}


# ---------- SQLite ----------

def sqlite_standin(src, dst, rows, rng):
    try:
        con = sqlite3.connect(f"file:{src}?mode=ro&immutable=1", uri=True)
        tables = con.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                             "AND sql IS NOT NULL ORDER BY name").fetchall()
    except sqlite3.DatabaseError as e:
        raise LeftOut(f"not a readable SQLite file ({e.__class__.__name__})")
    report = []
    if os.path.exists(dst):
        raise LeftOut("stand-in path already exists")
    out = sqlite3.connect(dst)
    for name, sql in tables:
        cols = [r[1] for r in con.execute(f'PRAGMA table_info("{name}")')]
        sample = con.execute(f'SELECT * FROM "{name}" LIMIT 5000').fetchall()
        profiles = rank_numbers([profile(c, [r[i] for r in sample]) for i, c in enumerate(cols)])
        out.execute(sql)
        marks = ",".join("?" for _ in cols)
        seen = set()
        for n in range(rows):
            row = invent_row(profiles, n, rng, rows)
            key = tuple(row)
            if key in seen:
                continue
            seen.add(key)
            try:
                out.execute(f'INSERT INTO "{name}" VALUES ({marks})', row)
            except sqlite3.IntegrityError:
                pass
        report.append({"name": name, "columns": profiles})
    for (sql,) in con.execute("SELECT sql FROM sqlite_master WHERE type IN ('index','view') AND sql IS NOT NULL"):
        try:
            out.execute(sql)
        except sqlite3.DatabaseError:
            pass
    out.commit()
    out.execute("VACUUM")
    out.close()
    con.close()
    return {"tables": report}


def make(src, dst, rows=8, seed=None):
    if os.path.abspath(src) == os.path.abspath(dst):
        raise LeftOut("refusing to write over the original")
    if os.path.islink(src) or not os.path.isfile(src):
        raise LeftOut("not a regular file")
    if os.path.getsize(src) > MAX_INPUT:
        raise LeftOut("too large to read safely")
    rng = random.Random(seed if seed is not None else 1)
    ext = os.path.splitext(src)[1].lower()
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    try:
        if ext in (".csv", ".tsv"):
            rep = csv_standin(src, dst, rows, rng)
        elif ext in (".xlsx", ".xlsm"):
            rep = xlsx_standin(src, dst, rows, rng)
        elif ext in (".db", ".sqlite", ".sqlite3", ".db3"):
            rep = sqlite_standin(src, dst, rows, rng)
        else:
            raise LeftOut(f"no stand-in maker for '{ext or 'no extension'}' files")
    except LeftOut:
        if os.path.exists(dst):
            os.remove(dst)
        raise
    except (UnicodeDecodeError, csv.Error, zipfile.BadZipFile, KeyError, ET.ParseError, ValueError) as e:
        if os.path.exists(dst):
            os.remove(dst)
        raise LeftOut(f"could not read it ({e.__class__.__name__})")
    groups = rep.get("sheets") or rep.get("tables") or []
    kept = [f"{g['name']}.{c['name']}" for g in groups for c in g["columns"] if c.get("labels")]
    personal = [f"{g['name']}.{c['name']}" for g in groups for c in g["columns"] if c["personal"]]
    return {"source": src, "standin": dst, "rows": rows, "structure": rep,
            "labels_kept": kept, "personal_columns": personal}


def record(pack, standin_path):
    import hashlib
    rec = os.path.join(pack, "STANDINS.json")
    data = {"standins": []}
    if os.path.exists(rec):
        with open(rec) as f:
            data = json.load(f)
    inner = os.path.relpath(os.path.abspath(standin_path), os.path.join(os.path.abspath(pack), "project"))
    with open(standin_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    data["standins"] = [e for e in data["standins"] if e["path"] != inner] + [{"path": inner, "sha256": digest}]
    with open(rec, "w") as f:
        json.dump(data, f, indent=1)


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    args = [a for a in argv if not a.startswith("--")]
    rows, pack = 8, None
    if "--pack" in argv:
        try:
            pack = argv[argv.index("--pack") + 1]
            args.remove(pack)
        except (IndexError, ValueError):
            print("standin: --pack needs the pack folder", file=sys.stderr)
            return 2
        inner = os.path.relpath(os.path.abspath(args[1] if len(args) > 1 else ""), os.path.join(os.path.abspath(pack), "project"))
        if len(args) != 2 or inner.startswith(".."):
            print("standin: with --pack, the stand-in must be written under <pack>/project/", file=sys.stderr)
            return 2
    if "--rows" in argv:
        try:
            rows = max(2, min(50, int(argv[argv.index("--rows") + 1])))
            args.remove(argv[argv.index("--rows") + 1])
        except (IndexError, ValueError):
            print("standin: --rows needs a number", file=sys.stderr)
            return 2
    if len(args) != 2:
        print("standin: give a data file and a stand-in path", file=sys.stderr)
        return 2
    try:
        res = make(args[0], args[1], rows)
    except LeftOut as e:
        print(json.dumps({"left_out": args[0], "reason": str(e)}) if "--json" in argv else f"left out: {e}")
        return 1
    if pack:
        record(pack, args[1])
    if "--json" in argv:
        print(json.dumps(res, indent=1, default=str))
    else:
        print(f"stand-in written: {res['standin']} ({rows} invented rows per sheet or table)")
        if res["labels_kept"]:
            print("category labels kept (show the owner): " + ", ".join(res["labels_kept"]))
        if res["personal_columns"]:
            print("personal columns (invented values): " + ", ".join(res["personal_columns"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
