import heapq

graph = {
    "S": [("A", 1), ("B", 4)],
    "A": [("C", 2)],
    "B": [("G", 5)],
    "C": [("G", 3)],
    "G": []
}

h_admissible = {"S": 5, "A": 4, "B": 4, "C": 2, "G": 0}
h_zero = {"S": 0, "A": 0, "B": 0, "C": 0, "G": 0}
h_overestimate = {"S": 5, "A": 4, "B": 4, "C": 10, "G": 0}


def check_consistency(g, h):
    consistent = True
    for u in g:
        for v, w in g[u]:
            if h[u] > w + h[v]:
                print(f"Consistency violated on edge {u}->{v}: h({u})={h[u]} > {w} + h({v})={w + h[v]}")
                consistent = False
    return consistent


def astar(g, h, start, goal):
    pq = [(h[start], 0, start, [start])]
    best = {start: 0}
    expansion_count = 0
    trace = []

    while pq:
        f, g_val, node, path = heapq.heappop(pq)
        trace.append((node, g_val, h[node], f))

        if node == goal:
            return g_val, path, expansion_count, trace

        if g_val > best.get(node, float("inf")):
            continue

        expansion_count += 1
        for nxt, w in g.get(node, []):
            ng = g_val + w
            if ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                heapq.heappush(pq, (ng + h[nxt], ng, nxt, path + [nxt]))

    return float("inf"), [], expansion_count, trace


if __name__ == "__main__":
    print("Consistency Check (Admissible Heuristic):", check_consistency(graph, h_admissible))
    print("Consistency Check (Overestimated Heuristic):", check_consistency(graph, h_overestimate))

    print("\n--- A* Search with Admissible Heuristic ---")
    cost, path, expansions, trace = astar(graph, h_admissible, "S", "G")
    print(f"Path: {path}, Cost: {cost}, Expanded Nodes Count: {expansions}")
    print("Expansion Trace (Node, g, h, f):", trace)

    print("\n--- UCS Search (Zero Heuristic) ---")
    u_cost, u_path, u_expansions, u_trace = astar(graph, h_zero, "S", "G")
    print(f"Path: {u_path}, Cost: {u_cost}, Expanded Nodes Count: {u_expansions}")
    print("Expansion Trace (Node, g, h, f):", u_trace)

    print("\n--- A* Search with Overestimated Heuristic (h(C)=10) ---")
    o_cost, o_path, o_expansions, o_trace = astar(graph, h_overestimate, "S", "G")
    print(f"Path: {o_path}, Cost: {o_cost}, Expanded Nodes Count: {o_expansions}")
    print("Expansion Trace (Node, g, h, f):", o_trace)

