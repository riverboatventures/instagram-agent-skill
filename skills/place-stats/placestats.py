#!/usr/bin/env python3
"""placestats: real, citable cost-of-living numbers for US cities/towns/CDPs.

Source: U.S. Census Bureau American Community Survey 5-year estimates, served by
the Census Reporter API (no key). Optional: Zillow Home Value Index (public
research CSV) for "typical home value".

    # every place in a county, ranked
    python3 placestats.py rank --state FL --county "Miami-Dade" --by income --top 5 --bottom 5
    # specific places
    python3 placestats.py show --state FL "Coral Gables" "Pinecrest" "Opa-locka"
    # add Zillow typical home value (downloads ~100MB once, cached)
    python3 placestats.py rank --state FL --county Miami-Dade --zillow
    # machine-readable
    ... --json out.json

Metrics: income = median household income (B19013), home = median home value
(B25077), rent = median gross rent (B25064), poverty = % below poverty (B17001),
pop = population (B01003). Every number comes with its margin of error.
"""
import argparse, csv, io, json, os, sys, time, urllib.request, urllib.parse
from pathlib import Path

API = "https://api.censusreporter.org/1.0/data/show/latest"
UA = "place-stats-skill/1.0"
ZILLOW = ("https://files.zillowstatic.com/research/public_csvs/zhvi/"
          "City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")
CACHE = Path(os.path.expanduser("~/.cache/place-stats")); CACHE.mkdir(parents=True, exist_ok=True)
STATES = dict(AL="01", AK="02", AZ="04", AR="05", CA="06", CO="08", CT="09", DE="10", DC="11", FL="12",
              GA="13", HI="15", ID="16", IL="17", IN="18", IA="19", KS="20", KY="21", LA="22", ME="23",
              MD="24", MA="25", MI="26", MN="27", MS="28", MO="29", MT="30", NE="31", NV="32", NH="33",
              NJ="34", NM="35", NY="36", NC="37", ND="38", OH="39", OK="40", OR="41", PA="42", RI="44",
              SC="45", SD="46", TN="47", TX="48", UT="49", VT="50", VA="51", WA="53", WV="54", WI="55",
              WY="56", PR="72")
TABLES = "B19013,B25077,B25064,B17001,B01003"
CAPS = {"income": 250001, "home": 2000001, "rent": 3501}   # Census top-codes


def get(url, timeout=90):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if i == 3:
                sys.exit(f"placestats: request failed: {e}\n  url: {url}\n"
                         "  (cloud sessions need api.censusreporter.org / files.zillowstatic.com allowed)")
            time.sleep(2 * (i + 1))


def acs(geo_ids):
    d = json.loads(get(f"{API}?table_ids={TABLES}&geo_ids={urllib.parse.quote(geo_ids, safe='|,')}"))
    if "error" in d:
        sys.exit(f"placestats: API error: {d['error']}")
    return d


def county_geoid(state, county):
    d = acs(f"050|04000US{STATES[state]}")
    want = county.lower().replace(" county", "").strip()
    for k, v in d["geography"].items():
        if v["name"].lower().replace(" county", "").split(",")[0].strip() == want:
            return k, v["name"]
    sys.exit(f"placestats: no county named {county!r} in {state}")


def rows_from(d):
    out = []
    for k, g in d["geography"].items():
        if not k.startswith("16000US") or k not in d["data"]:
            continue
        e = d["data"][k]
        val = lambda t, c: e[t]["estimate"].get(c)
        moe = lambda t, c: (e[t].get("error") or {}).get(c)
        pov_n, pov_d = val("B17001", "B17001002"), val("B17001", "B17001001")
        out.append({
            "geoid": k, "name": g["name"],
            "pop": val("B01003", "B01003001"),
            "income": val("B19013", "B19013001"), "income_moe": moe("B19013", "B19013001"),
            "home": val("B25077", "B25077001"), "home_moe": moe("B25077", "B25077001"),
            "rent": val("B25064", "B25064001"), "rent_moe": moe("B25064", "B25064001"),
            "poverty": round(100 * pov_n / pov_d, 1) if pov_n is not None and pov_d else None,
        })
    return out


def flags(r):
    f = []
    if r["pop"] is not None and r["pop"] < 2000:
        f.append("small pop")
    for m in ("income", "home", "rent"):
        v, e = r[m], r.get(m + "_moe")
        if v and e and e / v > 0.25:
            f.append(f"{m} ±{round(100 * e / v)}%")
        if v and v >= CAPS[m]:
            f.append(f"{m} top-coded")
    return f


def zillow_attach(rows, state):
    p = CACHE / "zhvi_city.csv"
    if not p.exists() or time.time() - p.stat().st_mtime > 20 * 86400:
        p.write_bytes(get(ZILLOW, timeout=600))
    with open(p, newline="") as fh:
        rd = csv.reader(fh); hdr = next(rd)
        last = len(hdr) - 1
        idx = {h: i for i, h in enumerate(hdr)}
        z = {}
        for row in rd:
            if row[idx["State"]] == state and row[last]:
                z[row[idx["RegionName"]].lower()] = float(row[last])
    for r in rows:
        r["zillow_home"] = z.get(r["name"].split(",")[0].lower())
    return hdr[last]


def money(v, cap=None):
    if v is None:
        return "n/a"
    s = f"${v:,.0f}"
    return s + "+" if cap and v >= cap else s


def table(rows, zcol):
    hdr = "| # | Place | Median household income | Median home value | Median rent | Poverty | Pop | Flags |"
    sep = "|---|---|---|---|---|---|---|---|"
    if zcol:
        hdr = hdr.replace("| Median rent", f"| Zillow typical home ({zcol}) | Median rent"); sep += "---|"
    lines = [hdr, sep]
    for i, r in enumerate(rows, 1):
        cells = [str(i), r["name"].replace(", ", ", "), money(r["income"], CAPS["income"]),
                 money(r["home"], CAPS["home"])]
        if zcol:
            cells.append(money(r.get("zillow_home")))
        cells += [money(r["rent"], CAPS["rent"]) + ("/mo" if r["rent"] else ""),
                  f"{r['poverty']}%" if r["poverty"] is not None else "n/a",
                  f"{r['pop']:,.0f}" if r["pop"] else "n/a", ", ".join(flags(r)) or ""]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    rk = sub.add_parser("rank"); rk.add_argument("--county", required=True)
    rk.add_argument("--by", default="income", choices=["income", "home", "rent", "poverty", "pop"])
    rk.add_argument("--top", type=int, default=5); rk.add_argument("--bottom", type=int, default=5)
    rk.add_argument("--exclude", nargs="*", default=[], help="place names to drop (e.g. military bases)")
    rk.add_argument("--min-pop", type=int, default=0)
    sh = sub.add_parser("show"); sh.add_argument("places", nargs="+")
    for p in (rk, sh):
        p.add_argument("--state", required=True, choices=sorted(STATES))
        p.add_argument("--zillow", action="store_true"); p.add_argument("--json")
    a = ap.parse_args()

    if a.cmd == "rank":
        cid, cname = county_geoid(a.state, a.county)
        d = acs(f"160|{cid}")
        rows = [r for r in rows_from(d) if r["name"].split(",")[0] not in a.exclude
                and (r["pop"] or 0) >= a.min_pop]
        missing = [r["name"] for r in rows if r[a.by] is None]
        rows = sorted([r for r in rows if r[a.by] is not None], key=lambda r: -r[a.by])
        zcol = zillow_attach(rows, a.state) if a.zillow else None
        print(f"# {cname}: {len(rows)} places ranked by {a.by}  ·  {d['release']['name']} ({d['release']['years']})\n")
        print(f"## Top {a.top}\n\n" + table(rows[:a.top], zcol))
        bot = rows[-a.bottom:][::-1]
        print(f"\n## Bottom {a.bottom} (lowest first)\n\n" + table(bot, zcol))
        if a.exclude:
            print(f"\nExcluded by request: {', '.join(a.exclude)}")
        if missing:
            print(f"No {a.by} estimate published for: {', '.join(missing)}")
        out = {"release": d["release"], "county": cname, "by": a.by, "top": rows[:a.top], "bottom": bot}
    else:
        allp = acs(f"160|04000US{STATES[a.state]}")
        idx = {g["name"].split(",")[0].lower(): k for k, g in allp["geography"].items()}
        ids = []
        for p in a.places:
            k = idx.get(p.lower())
            if not k:
                close = [n for n in idx if p.lower() in n][:5]
                print(f"! no Census place named {p!r} in {a.state}" + (f" (did you mean: {', '.join(close)})" if close else ""))
            else:
                ids.append(k)
        if not ids:
            sys.exit(1)
        d = acs(",".join(ids)); rows = rows_from(d)
        rows.sort(key=lambda r: ids.index(r["geoid"]))
        zcol = zillow_attach(rows, a.state) if a.zillow else None
        print(f"# {len(rows)} places  ·  {d['release']['name']} ({d['release']['years']})\n")
        print(table(rows, zcol)); out = {"release": d["release"], "places": rows}
    print("\nSource: U.S. Census Bureau, American Community Survey 5-year estimates, via Census Reporter."
          + (" Typical home value: Zillow Home Value Index." if a.zillow else ""))
    print("Flags: 'top-coded' = the Census caps the published value (income $250,001+, home $2,000,001+); "
          "'±N%' = margin of error over 25% of the estimate; 'small pop' = under 2,000 people.")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
