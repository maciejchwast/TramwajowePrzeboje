# Tramwajowe Przeboje

Projekt mający na celu symulację sieci tramwajowej na stworzonej sieci przystanków.

## Krakow tram network graph + route inspection

This repo also builds a real graph of the Krakow tram network (stops = nodes,
track segments = edges) from OpenStreetMap data, solves the **Route
Inspection Problem** (open/"path" Chinese Postman Problem) to find the
shortest one-way tram trip that rides every track segment at least once, and
renders the result on an interactive OpenStreetMap-based map.

### Usage

```bash
pip install -r requirements.txt
python3 src/fetch_osm_data.py       # downloads Krakow tram routes from OSM (Overpass API)
python3 run_route_inspection.py     # builds the graph, solves it, writes output/
```

Outputs:
- `output/route_plan.md` - step-by-step itinerary: which stop to start at,
  which tram line to ride on each leg, and at which stop to change lines.
- `output/map.html` - interactive map (OpenStreetMap basemap) showing the
  full tram network, the computed route colour-coded per line with
  direction arrows, and markers for the start stop, end stop, and every
  line change.

### How it works

- `src/fetch_osm_data.py` queries the Overpass API for all
  `route=tram` relations inside a bounding box around Krakow and caches the
  raw response to `data/overpass_tram.json`.
- `src/graph_build.py` turns each tram line's ordered stop sequence into
  graph edges (a physical track segment shared by several lines becomes one
  edge carrying the set of line refs that use it).
- `src/route_inspection.py` solves the open Chinese Postman Problem: it
  finds the pair of odd-degree stops to use as start/end and the minimum
  weight matching (shortest-path duplication) of the rest, then computes an
  Eulerian path over the augmented multigraph with networkx.
- `src/route_plan.py` walks that Eulerian path and greedily assigns a tram
  line to each edge (staying on the current line whenever possible) to
  produce human-readable ride legs and transfer points.
- `src/visualize.py` renders everything with `folium` on OpenStreetMap
  tiles.