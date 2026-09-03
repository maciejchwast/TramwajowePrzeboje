"""End-to-end pipeline: build the Krakow tram graph from cached OSM data,
solve the route-inspection (open Chinese Postman) problem, and produce a
human-readable route plan plus an interactive OSM map.

Usage:
    python3 src/fetch_osm_data.py      # once, needs internet access
    python3 run_route_inspection.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))

from graph_build import load_graph
from route_inspection import solve_open_chinese_postman
from route_plan import build_itinerary, format_itinerary
from visualize import render_map

OUT_DIR = pathlib.Path(__file__).resolve().parent / "output"


def main():
    g = load_graph()
    print(f"Loaded graph: {len(g.stops)} stops, {len(g.edges)} track segments, {len(g.lines)} lines")

    euler_edges, start, end, extra = solve_open_chinese_postman(g)
    print(f"Route-inspection walk: {len(euler_edges)} edge traversals, "
          f"{extra/1000:.2f} km retraced")

    legs = build_itinerary(g, euler_edges)
    plan_text = format_itinerary(g, legs, extra_km=extra / 1000)

    OUT_DIR.mkdir(exist_ok=True)
    plan_path = OUT_DIR / "route_plan.md"
    plan_path.write_text(plan_text)
    print(f"Wrote {plan_path}")

    map_path = render_map(g, euler_edges, legs)
    print(f"Wrote {map_path}")


if __name__ == "__main__":
    main()
