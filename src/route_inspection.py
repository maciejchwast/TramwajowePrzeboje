"""Route Inspection Problem (open/"path" Chinese Postman Problem) solver.

Given the tram network graph (nodes = stops, edges = physical track segments),
find the shortest walk that traverses every edge at least once. The walk does
not need to return to its start (open CPP): this is normally shorter than the
closed circuit version and matches "plan a one-way sightseeing tram trip".

Classic algorithm:
  1. Vertices of odd degree must have some incident edge duplicated (walked
     twice) so that an Eulerian walk becomes possible.
  2. If the graph already has 0 odd vertices -> Eulerian circuit exists.
     If it has exactly 2 -> Eulerian path exists between them already.
  3. Otherwise, find the minimum-weight perfect matching of the odd vertices
     (using shortest-path distance as the matching cost) that leaves exactly
     two odd vertices unmatched -- those two become the trip's start and end.
     We try every candidate unmatched pair and keep the cheapest overall
     matching, which is optimal for the open route-inspection problem.
  4. Duplicate the edges along each matched shortest path (add parallel
     copies) and compute an Eulerian path on the resulting multigraph.
"""
import itertools

import networkx as nx


def _build_networkx_multigraph(g):
    mg = nx.MultiGraph()
    for sid, info in g.stops.items():
        mg.add_node(sid, **info)
    for edge in g.edges.values():
        mg.add_edge(edge["a"], edge["b"], weight=edge["weight_m"], lines=edge["lines"])
    return mg


def _min_weight_perfect_matching(nodes, dist):
    """Exact minimum weight perfect matching on a complete graph over `nodes`
    using distances from `dist[u][v]`. `nodes` must have even length."""
    if not nodes:
        return []
    complete = nx.Graph()
    complete.add_nodes_from(nodes)
    max_d = max(dist[u][v] for u in nodes for v in nodes if u != v) if len(nodes) > 1 else 1.0
    for u, v in itertools.combinations(nodes, 2):
        # networkx max_weight_matching maximizes weight, so invert the cost.
        complete.add_edge(u, v, weight=max_d - dist[u][v])
    matching = nx.algorithms.matching.max_weight_matching(complete, maxcardinality=True)
    return list(matching)


def solve_open_chinese_postman(g):
    """Returns (euler_path_edges, start_node, end_node, extra_distance_m)

    euler_path_edges: list of (u, v) stop ids forming the walk in order.
    """
    mg = _build_networkx_multigraph(g)
    if not nx.is_connected(mg):
        largest = max(nx.connected_components(mg), key=len)
        mg = mg.subgraph(largest).copy()

    odd = [n for n in mg.nodes if mg.degree(n) % 2 == 1]

    # all-pairs shortest path distance & path restricted to odd vertices' needs
    dist = dict(nx.all_pairs_dijkstra_path_length(mg, weight="weight"))

    if len(odd) == 0:
        best_pair = None
        best_matching = []
        extra = 0.0
    elif len(odd) == 2:
        best_pair = tuple(odd)
        best_matching = []
        extra = 0.0
    else:
        best_pair = None
        best_matching = None
        best_cost = None
        for u, v in itertools.combinations(odd, 2):
            remaining = [n for n in odd if n not in (u, v)]
            matching = _min_weight_perfect_matching(remaining, dist)
            cost = sum(dist[a][b] for a, b in matching)
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_pair = (u, v)
                best_matching = matching
        extra = best_cost

    # duplicate edges along the shortest path of every matched pair
    aug = nx.MultiGraph()
    aug.add_nodes_from(mg.nodes(data=True))
    aug.add_edges_from(mg.edges(data=True))
    for u, v in best_matching:
        path = nx.dijkstra_path(mg, u, v, weight="weight")
        for a, b in zip(path, path[1:]):
            data = min(mg.get_edge_data(a, b).values(), key=lambda d: d["weight"])
            aug.add_edge(a, b, weight=data["weight"], lines=data["lines"])

    start, end = best_pair if best_pair else (next(iter(mg.nodes)), None)
    if end is None:
        # Eulerian circuit case: any start works, end == start.
        end = start
        euler_edges = list(nx.eulerian_circuit(aug, source=start))
    else:
        euler_edges = list(nx.eulerian_path(aug, source=start))

    return euler_edges, start, end, extra


if __name__ == "__main__":
    from graph_build import load_graph

    g = load_graph()
    euler_edges, start, end, extra = solve_open_chinese_postman(g)
    total = sum(g.edge(a, b)["weight_m"] for a, b in euler_edges)
    print(f"stops visited (walk length, edges): {len(euler_edges)}")
    print(f"start: {g.stops[start]['name']}  end: {g.stops[end]['name']}")
    print(f"extra (retraced) distance: {extra/1000:.2f} km")
    print(f"total route distance: {total/1000:.2f} km")
