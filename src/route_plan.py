"""Turn the Euler-path edge list into a human-readable ride plan: which tram
line to board, and at which stop to change to a different line.
"""


def _choose_line(prev_line, lines_serving_edge):
    """Prefer staying on the current line if it also serves this edge."""
    if prev_line is not None and prev_line in lines_serving_edge:
        return prev_line
    return sorted(lines_serving_edge)[0]


def build_itinerary(g, euler_edges):
    """Returns a list of legs:
        {"line": ref, "stops": [stop_id, ...]}
    Consecutive legs on a different line represent a transfer at the shared stop.
    """
    legs = []
    current_line = None
    current_stops = []

    for a, b in euler_edges:
        lines_here = g.edge(a, b)["lines"]
        line = _choose_line(current_line, lines_here)
        if line != current_line:
            if current_stops:
                legs.append({"line": current_line, "stops": current_stops})
            current_stops = [a]
            current_line = line
        current_stops.append(b)

    if current_stops:
        legs.append({"line": current_line, "stops": current_stops})

    return legs


def format_itinerary(g, legs, extra_km=0.0):
    out = []
    total_m = 0.0
    n_transfers = len(legs) - 1
    start_name = g.stops[legs[0]["stops"][0]]["name"]
    end_name = g.stops[legs[-1]["stops"][-1]]["name"]

    out.append("# Krakow tram network - full-network sightseeing route\n")
    out.append(f"Start: **{start_name}**")
    out.append(f"End:   **{end_name}**")
    out.append(f"Line changes: **{n_transfers}**\n")

    for i, leg in enumerate(legs, start=1):
        stops = leg["stops"]
        leg_len = sum(g.edge(a, b)["weight_m"] for a, b in zip(stops, stops[1:]))
        total_m += leg_len
        line_name = g.lines.get(leg["line"], {}).get("name", leg["line"])
        out.append(f"## Leg {i}: tram line **{leg['line']}** ({line_name}) - {leg_len/1000:.2f} km, {len(stops)} stops")
        out.append(f"Board at **{g.stops[stops[0]]['name']}**")
        if len(stops) > 2:
            via = ", ".join(g.stops[s]["name"] for s in stops[1:-1])
            out.append(f"Via: {via}")
        if i < len(legs):
            out.append(f"Get off / change tram at **{g.stops[stops[-1]]['name']}** -> board line {legs[i]['line']}\n")
        else:
            out.append(f"Get off at **{g.stops[stops[-1]]['name']}** (journey ends here)\n")

    out.append(f"\n**Total distance ridden: {total_m/1000:.2f} km** "
                f"(network length + {extra_km:.2f} km ridden twice to reach every track segment)")
    return "\n".join(out)
