"""Fetch Krakow tram route relations (stops + line membership) from OpenStreetMap
via the Overpass API and cache the raw response to data/overpass_tram.json.

Usage:
    python3 src/fetch_osm_data.py
"""
import json
import pathlib
import sys
import time

import requests

# Bounding box loosely covering the Krakow tram network (incl. Nowa Huta, Bronowice,
# Krowodrza, Podgorze, Wzgorza Krzeslawickie loop).
BBOX = (49.97, 19.75, 50.13, 20.10)  # south, west, north, east

QUERY = """
[out:json][timeout:180];
rel["route"="tram"]["type"="route"]({s},{w},{n},{e});
out body geom;
""".format(s=BBOX[0], w=BBOX[1], n=BBOX[2], e=BBOX[3])

# Public Overpass API mirrors to try, in order.
MIRRORS = [
    "https://overpass.monicz.dev/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

HEADERS = {"User-Agent": "TramwajowePrzeboje-KrakowTramGraph/1.0 (educational routing project)"}

OUT_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "overpass_tram.json"


def fetch(timeout=240):
    last_err = None
    for url in MIRRORS:
        print(f"Trying {url} ...", file=sys.stderr)
        try:
            resp = requests.post(url, data={"data": QUERY}, headers=HEADERS, timeout=timeout)
        except requests.exceptions.RequestException as exc:
            print(f"  failed: {exc}", file=sys.stderr)
            last_err = exc
            continue
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            last_err = RuntimeError(f"HTTP {resp.status_code} from {url}")
            continue
        data = resp.json()
        if not data.get("elements"):
            print("  empty result, trying next mirror", file=sys.stderr)
            continue
        return data
    raise RuntimeError(f"All Overpass mirrors failed. Last error: {last_err}")


def main():
    data = fetch()
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    n_relations = sum(1 for e in data["elements"] if e["type"] == "relation")
    print(f"Saved {n_relations} tram route relations to {OUT_PATH}")


if __name__ == "__main__":
    main()
