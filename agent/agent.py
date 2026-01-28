"""Q-Learning agent for Snake game."""

import random
from typing import Dict, List, Tuple

# Type alias for Q-Table
QTable = Dict[Tuple, List[float]]


def init_state(q: QTable, state: Tuple) -> None:
    """Initialize state in Q-table if not present."""
    if state not in q:
        q[state] = [0.0, 0.0, 0.0, 0.0]


def safe_actions_from_state(state: Tuple) -> List[int]:
    """
    Filter actions to avoid immediate danger (wall/snake at distance 1).
    State format: ((sym, dist), (sym, dist), (sym, dist), (sym, dist))
    Order: UP, RIGHT, DOWN, LEFT
    """
    safe = []
    for action in range(4):
        sym, dist = state[action]
        # Éviter mur ou corps à distance 1
        if not (dist == 1 and sym in ("W", "S")):
            safe.append(action)
    return safe if safe else [0, 1, 2, 3]


def choose_action(q: QTable, state: Tuple, epsilon: float, use_safety: bool) -> int:
    """Choose action using epsilon-greedy policy."""
    if random.random() < epsilon:
        if use_safety:
            safe = safe_actions_from_state(state)
            return random.choice(safe)
        return random.randint(0, 3)

    values = q[state]
    max_v = max(values)
    best = [i for i, v in enumerate(values) if v == max_v]

    if use_safety:
        safe = safe_actions_from_state(state)
        best_safe = [a for a in best if a in safe]
        return random.choice(best_safe) if best_safe else random.choice(best)

    return random.choice(best)


def update_q(q: QTable, state: Tuple, action: int, reward: float,
             next_state: Tuple, alpha: float, gamma: float) -> None:
    """Update Q-value using Bellman equation."""
    best_next = max(q[next_state])
    q[state][action] += alpha * (reward + gamma * best_next - q[state][action])
