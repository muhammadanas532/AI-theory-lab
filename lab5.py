import math

def minimax(cur_depth, node_index, is_max, scores, target_depth, counter):
    if cur_depth == target_depth:
        counter[0] += 1
        return scores[node_index]

    if is_max:
        left = minimax(cur_depth + 1, node_index * 2, False, scores, target_depth, counter)
        right = minimax(cur_depth + 1, node_index * 2 + 1, False, scores, target_depth, counter)
        return max(left, right)
    else:
        left = minimax(cur_depth + 1, node_index * 2, True, scores, target_depth, counter)
        right = minimax(cur_depth + 1, node_index * 2 + 1, True, scores, target_depth, counter)
        return min(left, right)


def alphabeta(cur_depth, node_index, is_max, scores, target_depth, alpha, beta, counter):
    if cur_depth == target_depth:
        counter[0] += 1
        return scores[node_index]

    if is_max:
        value = float("-inf")
        for i in range(2):
            val = alphabeta(cur_depth + 1, node_index * 2 + i, False, scores, target_depth, alpha, beta, counter)
            value = max(value, val)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float("inf")
        for i in range(2):
            val = alphabeta(cur_depth + 1, node_index * 2 + i, True, scores, target_depth, alpha, beta, counter)
            value = min(value, val)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def run_experiment(leaf_scores):
    depth = math.ceil(math.log2(len(leaf_scores)))
    padded_scores = list(leaf_scores) + [0] * (2**depth - len(leaf_scores))

    minimax_counter = [0]
    val_minimax = minimax(0, 0, True, padded_scores, depth, minimax_counter)

    ab_counter = [0]
    val_ab = alphabeta(0, 0, True, padded_scores, depth, float("-inf"), float("inf"), ab_counter)

    print("Scores:", padded_scores)
    print(f"Minimax Value: {val_minimax} | Evaluated Leaves: {minimax_counter[0]}")
    print(f"Alpha-Beta Value: {val_ab} | Evaluated Leaves: {ab_counter[0]}")


if __name__ == "__main__":
    print("--- Test 1: Standard Tree ---")
    tree1 = [3, 5, 2, 9, 0, 7]
    run_experiment(tree1)

    print("\n--- Test 2: Complete Binary Tree ---")
    tree2 = [3, 5, 2, 9, 3, 5, 2, 9]
    run_experiment(tree2)

    print("\n--- Test 3: Reordered Tree (Pruning Comparison) ---")
    tree3 = [2, 9, 3, 5, 9, 2, 5, 3]
    run_experiment(tree3)

