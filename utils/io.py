"""Utility functions for saving and loading models."""

import os
import pickle
from typing import Dict, List, Tuple, Any

QTable = Dict[Tuple, List[float]]


def save_model(q: QTable, path: str, episodes: int = 0) -> None:
    """Save Q-table to file with metadata."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    
    # Sauvegarder Q-table + metadata
    data = {
        "q_table": q,
        "episodes": episodes,
        "states_count": len(q),
    }
    
    with open(path, "wb") as f:
        pickle.dump(data, f)
    print(f"Modele sauvegarde: {path} ({len(q)} etats, {episodes} episodes)")


def load_model(path: str) -> Tuple[QTable, int]:
    """Load Q-table from file with metadata.
    
    Returns:
        Tuple of (Q-table, total_episodes)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier non trouve: {path}")
    
    with open(path, "rb") as f:
        data = pickle.load(f)
    
    # Support ancien format (juste Q-table) et nouveau format (dict avec metadata)
    if isinstance(data, dict) and "q_table" in data:
        q = data["q_table"]
        episodes = data.get("episodes", 0)
    else:
        # Ancien format: data est directement la Q-table
        q = data
        # Essayer de deviner depuis le nom du fichier
        episodes = 0
        name = os.path.basename(path)
        if "sess" in name:
            try:
                episodes = int(name.split("sess")[0])
            except ValueError:
                episodes = 0
    
    print(f"\n{'='*50}")
    print(f"  MODELE CHARGE")
    print(f"{'='*50}")
    print(f"  Fichier: {path}")
    print(f"  Episodes d'entrainement: {episodes}")
    print(f"  Etats dans Q-table: {len(q)}")
    print(f"{'='*50}\n")
    
    return q, episodes
