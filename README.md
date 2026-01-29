# Learn2Slither

**Reinforcement Learning** - Un serpent qui apprend à se comporter dans un environnement par essai-erreur.

# Description

Ce projet implémente un agent intelligent contrôlant un serpent sur un plateau de jeu 10x10. L'agent utilise l'algorithme **Q-Learning** pour apprendre à :
- Manger les pommes vertes
- Éviter les pommes rouges
- Éviter les murs et son propre corps
- Survivre le plus longtemps possible

**Objectif** : Atteindre une longueur de **10 ou plus** et survivre le plus longtemps possible.

## 🏗️ Structure du Projet

```
Learn2Slither/
├── main.py                 # Point d'entrée principal
├── Board/
│   └── environment.py      # Environnement du jeu (plateau, snake, pommes)
├── agent/
│   └── agent.py            # Agent Q-Learning (Q-table, actions, rewards)
├── modes/
│   └── game_modes.py       # Modes de jeu (train, evaluate, visual)
├── render/
│   ├── display.py          # Affichage graphique Pygame
│   └── ascii.py            # Affichage ASCII terminal
├── utils/
│   └── io.py               # Sauvegarde/chargement des modèles
└── models/                 # Modèles entraînés
    ├── 1sess.pkl
    ├── 10sess.pkl
    ├── 100sess.pkl
    ├── 5000sess.pkl
    ├── visiononly_20k.pkl
    └── Snake_3.0.plk
```

# Utilisation

### Mode Entraînement (`--train`)

Entraîne un nouveau modèle avec le nombre d'épisodes spécifié.

```bash
# Entraîner 100 épisodes et sauvegarder
python3 main.py --train --episodes 100 --save models/100sess.pkl

# Entraîner 5000 épisodes
python3 main.py --train --episodes 5000 --save models/5000sess.pkl

# Entraîner 50000 épisodes (recommandé pour de bonnes performances)
python3 main.py --train --episodes 50000 --save models/mon_model.pkl
```

### Mode Évaluation (`--evaluate`)

Évalue un modèle sans apprentissage (mode `dontlearn`).

```bash
# Évaluer sur 100 parties
python3 main.py --evaluate --load models/5000sess.pkl --games 100

# Évaluer le meilleur modèle
python3 main.py --evaluate --load models/Snake_3.0.plk --games 100

# Désactiver le filtre de sécurité
python3 main.py --evaluate --load models/5000sess.pkl --games 100 --no-safety
```

### Mode Visualisation (`--visual`)

Visualise le serpent en action.

```bash
# Visualisation en ASCII (terminal)
python3 main.py --visual --load models/Snake_3.0.plk

# Visualisation avec fenêtre graphique Pygame
python3 main.py --visual --load models/Snake_3.0.plk --window

# Ajuster la vitesse (FPS)
python3 main.py --visual --load models/Snake_3.0.plk --window --fps 5

# Mode pas-à-pas (appuyer sur ENTRÉE pour avancer)
python3 main.py --visual --load models/Snake_3.0.plk --window --step
```

## ⚙️ Arguments

| Argument | Description |
|----------|-------------|
| `--train` | Mode entraînement |
| `--evaluate` | Mode évaluation (sans apprentissage) |
| `--visual` | Mode visualisation |
| `--load <path>` | Charger un modèle existant |
| `--save <path>` | Sauvegarder le modèle entraîné |
| `--episodes <n>` | Nombre d'épisodes d'entraînement (défaut: 2000) |
| `--games <n>` | Nombre de parties pour l'évaluation (défaut: 100) |
| `--window` | Affichage graphique Pygame |
| `--fps <n>` | Vitesse d'affichage (défaut: 10) |
| `--step` | Mode pas-à-pas |
| `--no-safety` | Désactive le filtre de sécurité |

## 📊 Performances des Modèles

Les performances varient en fonction du nombre d'épisodes d'entraînement :

| Modèle | Épisodes | États Q | Moy. | Max | ≥10 |
|--------|----------|---------|------|-----|-----|
| `1sess.pkl` | 1 | 1 | 3.00 | 4 | 0% |
| `10sess.pkl` | 10 | 20 | 3.12 | 4 | 0% |
| `100sess.pkl` | 100 | 164 | 3.18 | 4 | 0% |
| `5000sess.pkl` | 5,000 | 2,046 | 7.68 | 19 | 32% |
| `visiononly_20k.pkl` | 50,000 | 3,543 | 15.14 | 30 | 70% |
| **`Snake_3.0.plk`** | **500,000** | **5,098** | **18.16** | **40** | **76%** |

Remarque : Les modèles avec peu d'entraînement (1, 10, 100 sessions) montrent des performances limitées. C'est normal et démontre l'importance de l'apprentissage progressif. Pour de bonnes performances, utilisez un modèle avec **5000+ épisodes**.

# Améliorations du State

L'intelligence de l'IA a été améliorée grâce à plusieurs optimisations de la représentation d'état :

### Vision du Snake
Le snake voit dans les **4 directions** (UP, RIGHT, DOWN, LEFT) depuis sa tête :
- `G` = Pomme verte
- `R` = Pomme rouge
- `S` = Corps du snake
- `W` = Mur

# Bucketing de Distance
Les distances sont regroupées en **3 catégories** pour réduire l'espace d'états :
- `1` = Très proche (1-2 cases)
- `2` = Proche (3-4 cases)
- `3` = Loin (5+ cases)

# Reward Shaping

- Manger pomme verte : +20
- Manger pomme rouge : -20
- Game Over (mur/collision/longueur 0) : -100
- Timeout (trop de steps sans manger) : -50
- Se diriger vers une pomme verte visible : +0.2
- Se diriger vers un danger immédiat : -1.0

## 🎯 Exemples de Commandes

```bash
# Exemple complet : entraîner, puis évaluer
python3 main.py --train --episodes 10000 --save models/nouveau.pkl
python3 main.py --evaluate --load models/nouveau.pkl --games 100

# Voir le meilleur modèle en action
python3 main.py --visual --load models/Snake_3.0.plk --window --fps 8

# Mode pas-à-pas pour observer chaque décision
python3 main.py --visual --load models/Snake_3.0.plk --step
```

