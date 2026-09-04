"""Render the Krakow tram network and the computed route-inspection walk on
an OpenStreetMap basemap using folium, saved as an interactive HTML map.
"""
import pathlib

import folium
from folium import plugins

OUT_PATH = pathlib.Path(__file__).resolve().parent.parent / "output" / "map.html"


def _centroid(g):
    lats = [s["lat"] for s in g.stops.values()]
    lons = [s["lon"] for s in g.stops.values()]
    return sum(lats) / len(lats), sum(lons) / len(lons)


def render_map(g, euler_edges, legs, out_path=OUT_PATH):
    lat, lon = _centroid(g)
    m = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap", control_scale=True)

    # 1. faint layer: the whole physical network
    network_layer = folium.FeatureGroup(name="Full tram network", show=True)
    for edge in g.edges.values():
        a, b = g.stops[edge["a"]], g.stops[edge["b"]]
        folium.PolyLine(
            [(a["lat"], a["lon"]), (b["lat"], b["lon"])],
            color="#9aa0a6", weight=2, opacity=0.6,
            tooltip="Lines: " + ", ".join(sorted(edge["lines"])),
        ).add_to(network_layer)
    network_layer.add_to(m)

    # 2. stop markers
    stops_layer = folium.FeatureGroup(name="Stops", show=True)
    for sid, s in g.stops.items():
        folium.CircleMarker(
            (s["lat"], s["lon"]), radius=2.5, color="#4285f4", fill=True,
            fill_opacity=0.9, tooltip=s["name"],
        ).add_to(stops_layer)
    stops_layer.add_to(m)

    # 3. the computed route, colour-coded per line, with sequence order + arrows
    palette = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#46f0f0",
               "#f032e6", "#bcf60c", "#fabebe", "#008080", "#e6beff", "#9a6324",
               "#800000", "#808000", "#000075", "#a9a9a9"]
    line_colour = {}

    def colour_for(line_ref):
        if line_ref not in line_colour:
            line_colour[line_ref] = palette[len(line_colour) % len(palette)]
        return line_colour[line_ref]

    route_layer = folium.FeatureGroup(name="Computed route (visits every track segment)", show=True)
    order = 0
    for leg in legs:
        stops = leg["stops"]
        colour = colour_for(leg["line"])
        pts = [(g.stops[s]["lat"], g.stops[s]["lon"]) for s in stops]
        pl = folium.PolyLine(pts, color=colour, weight=4, opacity=0.85,
                              tooltip=f"Line {leg['line']}")
        pl.add_to(route_layer)
        plugins.PolyLineTextPath(pl, "  ►  ", repeat=True, offset=6,
                                  attributes={"fill": colour, "font-weight": "bold"}).add_to(route_layer)
        order += 1

    route_layer.add_to(m)

    # 4. start / end / transfer markers
    markers_layer = folium.FeatureGroup(name="Start / transfers / end", show=True)
    start_stop = legs[0]["stops"][0]
    end_stop = legs[-1]["stops"][-1]
    s = g.stops[start_stop]
    folium.Marker((s["lat"], s["lon"]), tooltip=f"START: {s['name']}",
                  icon=folium.Icon(color="green", icon="play")).add_to(markers_layer)
    e = g.stops[end_stop]
    folium.Marker((e["lat"], e["lon"]), tooltip=f"END: {e['name']}",
                  icon=folium.Icon(color="red", icon="stop")).add_to(markers_layer)
    for i, leg in enumerate(legs[:-1], start=1):
        tid = leg["stops"][-1]
        t = g.stops[tid]
        next_line = legs[i]["line"]
        folium.Marker(
            (t["lat"], t["lon"]),
            tooltip=f"Change to line {next_line} at {t['name']}",
            icon=folium.Icon(color="orange", icon="exchange", prefix="fa"),
        ).add_to(markers_layer)
    markers_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    out_path.parent.mkdir(exist_ok=True)
    m.save(str(out_path))
    return out_path
