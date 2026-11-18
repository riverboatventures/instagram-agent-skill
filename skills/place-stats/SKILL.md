---
name: place-stats
description: >-
  Pull real, citable cost-of-living and wealth numbers for US cities, towns and
  neighborhoods (Census places/CDPs): median household income, median home
  value, median rent, poverty rate and population with margins of error, plus
  Zillow's typical home value. Ranks every place in a county to find the
  richest/poorest, most/least expensive. Use for "richest neighborhoods in X",
  "poorest places in X", "cost of living in X", "median income/rent/home value
  for X", carousel or post stats, or any time a slide needs a number about a
  place that must not be made up.
---

# place-stats

One script, no API key:

```bash
python3 ~/.claude/skills/place-stats/placestats.py rank --state FL --county "Miami-Dade" --by income --top 5 --bottom 5 --zillow
python3 ~/.claude/skills/place-stats/placestats.py show --state FL "Coral Gables" "Opa-locka" --zillow
```

- `rank`: every Census place in the county, sorted by `--by income|home|rent|poverty|pop`.
  `--exclude "Homestead Base"` drops non-neighborhoods (military bases, prisons,
  industrial-only towns if you decide so); `--min-pop N` drops tiny places.
- `show`: named places in a state. Unknown names print close matches.
- `--zillow`: adds Zillow Home Value Index (typical home value, latest month).
  Downloads a ~100 MB public CSV once, cached 20 days in `~/.cache/place-stats`.
- `--json out.json`: structured output for building slides.

## Sources (put these on the slide or in the caption)

- **U.S. Census Bureau, American Community Survey 5-year estimates**, the
  latest release (the script prints which years), via the Census Reporter API.
- **Zillow Home Value Index** when `--zillow` is used.

## Read the flags before you publish a number

- **top-coded**: the Census will not publish above $250,001 income or
  $2,000,001 home value. Write "$250,001+" / "$2M+", never the bare number.
- **±N%**: the margin of error is over a quarter of the estimate. Two places
  within each other's margin are a tie; say so or do not rank them against
  each other.
- **small pop**: under 2,000 people. Fine to show, but name the size.
- **n/a**: the Census did not publish it (too few households). Do not fill it
  from somewhere else without saying where.

## Rules

- These are Census *places* (incorporated cities and CDPs). City-of-X
  neighborhoods like Overtown or Brickell are not Census places. For those you
  need tract data, so say the list is "places in X County", not "neighborhoods".
- Always run `rank` before claiming "the top 5" or "the poorest". Hand-picked
  lists are usually wrong. The first draft of the Miami list was wrong on 3 of 10.
- Never invent or round up a number to make a slide read better.

## When the network is blocked

Cloud sessions need `api.censusreporter.org` (and `files.zillowstatic.com` for
`--zillow`) on the allowed hosts. `api.census.gov` itself now requires a key in
the URL, so this script does not use it.
