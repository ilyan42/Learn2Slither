"""Agent package for Learn2Slither."""

from agent.agent import (
    QTable,
    init_state,
    safe_actions_from_state,
    choose_action,
    update_q,
)

__all__ = [
    "QTable",
    "init_state",
    "safe_actions_from_state",
    "choose_action",
    "update_q",
]
