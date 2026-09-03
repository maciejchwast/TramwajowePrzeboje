"""Turn the Euler-path edge list into a human-readable ride plan: which tram
line to board, and at which stop to change to a different line.
"""


def _assign_lines_minimizing_transfers(candidates):
    """Given, for each edge in the walk (in order), the set of line refs that
    serve it, choose one line per edge minimizing the number of times the
    chosen line changes between consecutive edges.

    This is solved exactly with a simple DP: dp[i][line] = minimum
    transfers among any valid assignment of edges 0..i that ends edge i on
    `line`. At each step a line can either continue from itself at i-1
    (free) or switch from whichever line was cheapest at i-1 (+1 transfer).
    """
    n = len(candidates)
    dp_prev = {line: 0 for line in candidates[0]}
    parent = [None] * n
    parent[0] = {line: None for line in candidates[0]}

    for i in range(1, n):
        min_prev_line = min(dp_prev, key=dp_prev.get)
        min_prev_cost = dp_prev[min_prev_line]
        dp_cur = {}
        parent[i] = {}
        for line in candidates[i]:
            continue_cost = dp_prev.get(line, float("inf"))
            switch_cost = min_prev_cost + 1
            if continue_cost <= switch_cost:
                dp_cur[line] = continue_cost
                parent[i][line] = line
            else:
                dp_cur[line] = switch_cost
                parent[i][line] = min_prev_line
        dp_prev = dp_cur

    best_line = min(dp_prev, key=dp_prev.get)
    assignment = [None] * n
    line = best_line
    for i in range(n - 1, -1, -1):
        assignment[i] = line
        line = parent[i][line]

    return assignment


def build_itinerary(g, euler_edges):
    """Returns a list of legs:
        {"line": ref, "stops": [stop_id, ...]}
    Consecutive legs on a different line represent a transfer at the shared stop.
    """
    candidates = [g.edge(a, b)["lines"] for a, b in euler_edges]
    line_per_edge = _assign_lines_minimizing_transfers(candidates)

    legs = []
    current_line = None
    current_stops = []

    for (a, b), line in zip(euler_edges, line_per_edge):
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
