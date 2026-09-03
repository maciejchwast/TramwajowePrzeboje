"""Build a graph of the Krakow tram network from cached Overpass (OSM) data.

Nodes  = tram stops (stop_position nodes shared by all lines serving that stop).
Edges  = physical track segments directly connecting two consecutive stops on
         at least one tram line. Parallel segments used by several lines are
         merged into a single edge carrying the set of line refs that use it.
"""
import json
import math
import pathlib
from collections import defaultdict

DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "overpass_tram.json"

STOP_ROLES = {"stop", "stop_entry_only", "stop_exit_only"}
PLATFORM_ROLES = {"platform", "platform_entry_only", "platform_exit_only"}


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class TramGraph:
    def __init__(self):
        self.stops = {}          # stop_id -> {"name", "lat", "lon"}
        self.edges = {}          # frozenset({a,b}) -> {"weight_m", "lines": set(), "a":, "b":}
        self.lines = {}          # ref -> {"name", "color", "stop_sequence": [stop_id,...]}
        self.adj = defaultdict(set)  # stop_id -> set(stop_id)

    def add_stop(self, stop_id, name, lat, lon):
        if stop_id not in self.stops:
            self.stops[stop_id] = {"name": name, "lat": lat, "lon": lon}

    def add_edge(self, a, b, line_ref):
        if a == b:
            return
        key = frozenset((a, b))
        if key not in self.edges:
            dist = haversine_m(self.stops[a]["lat"], self.stops[a]["lon"],
                                self.stops[b]["lat"], self.stops[b]["lon"])
            self.edges[key] = {"weight_m": dist, "lines": set(), "a": a, "b": b}
        self.edges[key]["lines"].add(line_ref)
        self.adj[a].add(b)
        self.adj[b].add(a)

    def neighbors(self, stop_id):
        return self.adj[stop_id]

    def edge(self, a, b):
        return self.edges[frozenset((a, b))]


def _stop_identity(member):
    """Return (id, name, lat, lon) for a relation member that represents a stop."""
    ref = member["ref"]
    lat = member.get("lat")
    lon = member.get("lon")
    name = member.get("tags", {}).get("name") if "tags" in member else None
    return ref, name, lat, lon


def load_graph(path=DATA_PATH):
    raw = json.loads(pathlib.Path(path).read_text())
    node_index = {e["id"]: e for e in raw["elements"] if e["type"] == "node"}

    g = TramGraph()
    n_lines = 0
    for el in raw["elements"]:
        if el["type"] != "relation":
            continue
        tags = el.get("tags", {})
        ref = tags.get("ref") or tags.get("name") or str(el["id"])
        name = tags.get("name", ref)
        colour = tags.get("colour")

        # collect ordered stop-position nodes (fallback to platforms if none tagged)
        stop_members = [m for m in el["members"] if m["type"] == "node" and m.get("role") in STOP_ROLES]
        if not stop_members:
            stop_members = [m for m in el["members"] if m["type"] == "node" and m.get("role") in PLATFORM_ROLES]
        if len(stop_members) < 2:
            continue

        seq = []
        for m in stop_members:
            sid, mname, lat, lon = _stop_identity(m)
            if lat is None or lon is None:
                node = node_index.get(sid)
                if node is None:
                    continue
                lat, lon = node["lat"], node["lon"]
            if mname is None:
                node = node_index.get(sid)
                mname = node.get("tags", {}).get("name") if node else None
            mname = mname or f"stop {sid}"
            g.add_stop(sid, mname, lat, lon)
            seq.append(sid)

        if len(seq) < 2:
            continue

        for a, b in zip(seq, seq[1:]):
            g.add_edge(a, b, ref)

        g.lines[ref] = {"name": name, "colour": colour, "stop_sequence": seq, "osm_id": el["id"]}
        n_lines += 1

    return g


if __name__ == "__main__":
    g = load_graph()
    degrees = {s: len(g.neighbors(s)) for s in g.stops}
    odd = [s for s, d in degrees.items() if d % 2 == 1]
    total_len_km = sum(e["weight_m"] for e in g.edges.values()) / 1000
    print(f"lines: {len(g.lines)}")
    print(f"stops (nodes): {len(g.stops)}")
    print(f"track segments (edges): {len(g.edges)}")
    print(f"total network length: {total_len_km:.1f} km")
    print(f"odd-degree stops: {len(odd)}")
