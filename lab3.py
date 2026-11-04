from collections import deque
import heapq

graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["G"],
    "F": [],
    "G": []
}

weighted_graph = {
    "A": [("B", 1), ("C", 2)],
    "B": [("D", 5), ("E", 1)],
    "C": [("F", 5), ("G", 10)],
    "D": [],
    "E": [("G", 1)],
    "F": [],
    "G": []
}


def bfs(start, goal):
    queue = deque([(start, [start])])
    visited = []
    seen = {start}
    while queue:
        node, path = queue.popleft()
        visited.append(node)
        if node == goal:
            return path, visited
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None, visited


def dfs(start, goal):
    stack = [(start, [start])]
    visited = []
    seen = set()
    while stack:
        node, path = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        visited.append(node)
        if node == goal:
            return path, visited
        for neighbor in reversed(graph.get(node, [])):
            if neighbor not in seen:
                stack.append((neighbor, path + [neighbor]))
    return None, visited


def dls(node, goal, limit, path):
    if node == goal:
        return "FOUND", path
    if limit <= 0:
        return "CUTOFF", None
    cutoff_occurred = False
    for neighbor in graph.get(node, []):
        if neighbor not in path:
            status, res_path = dls(neighbor, goal, limit - 1, path + [neighbor])
            if status == "FOUND":
                return "FOUND", res_path
            if status == "CUTOFF":
                cutoff_occurred = True
    if cutoff_occurred:
        return "CUTOFF", None
    return "FAILURE", None


def iddfs(start, goal, max_depth):
    for depth in range(1, max_depth + 1):
        status, path = dls(start, goal, depth, [start])
        print(f"IDDFS limit {depth}: status={status}, path={path}")
        if status == "FOUND":
            return path
    return None


def ucs(start, goal):
    pq = [(0, start, [start])]
    visited = []
    best_cost = {start: 0}
    while pq:
        cost, node, path = heapq.heappop(pq)
        visited.append(node)
        if node == goal:
            return path, cost, visited
        if cost > best_cost.get(node, float("inf")):
            continue
        for neighbor, weight in weighted_graph.get(node, []):
            new_cost = cost + weight
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))
    return None, float("inf"), visited


def bfs_weighted(start, goal):
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        node, path = queue.popleft()
        if node == goal:
            cost = 0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                for nxt, w in weighted_graph[u]:
                    if nxt == v:
                        cost += w
                        break
            return path, cost
        for neighbor, _ in weighted_graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None, 0


if __name__ == "__main__":
    bfs_path, bfs_visited = bfs("A", "G")
    print("BFS Path:", bfs_path)
    print("BFS Visited Order:", bfs_visited)

    dfs_path, dfs_visited = dfs("A", "G")
    print("DFS Path:", dfs_path)
    print("DFS Visited Order:", dfs_visited)

    print("\n--- DLS Tests ---")
    for limit in [1, 2, 3, 4]:
        status, path = dls("A", "G", limit, ["A"])
        print(f"DLS limit {limit}: status={status}, path={path}")

    print("\n--- IDDFS Execution ---")
    iddfs("A", "G", 4)

    print("\n--- UCS vs BFS on Weighted Graph ---")
    ucs_path, ucs_cost, ucs_visited = ucs("A", "G")
    print(f"UCS Path: {ucs_path}, Cost: {ucs_cost}, Visited: {ucs_visited}")

    bfs_w_path, bfs_w_cost = bfs_weighted("A", "G")
    print(f"BFS Path: {bfs_w_path}, Cost: {bfs_w_cost}")

