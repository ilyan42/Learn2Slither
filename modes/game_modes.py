"""Game modes for Learn2Slither."""

import time
import random
from typing import Optional

from Board.environment import Environment
from render.display import PygameRenderer
from render.ascii import display_grid_ascii, get_key, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from agent.agent import QTable, init_state, choose_action, update_q
from utils.io import save_model, load_model

# Constants
ACTIONS = [Environment.UP, Environment.RIGHT, Environment.DOWN, Environment.LEFT]
ACTION_NAMES = ["UP", "RIGHT", "DOWN", "LEFT"]


def train_mode(
    episodes: int,
    save_path: str,
    alpha: float = 0.2,
    gamma: float = 0.95,
    eps_start: float = 0.4,
    eps_end: float = 0.05,
) -> None:
    """Train the agent using Q-learning."""
    Q: QTable = {}

    decay_episodes = int(episodes * 0.7)
    best_len = 0

    print(f"\n{'='*60}")
    print(f"  MODE ENTRAINEMENT - {episodes} episodes")
    print(f"{'='*60}")
    print(f"  alpha={alpha} | gamma={gamma} | eps {eps_start}->{eps_end}")
    print(f"{'='*60}\n")

    for ep in range(1, episodes + 1):
        env = Environment()
        steps = 0

        epsilon = max(
            eps_end,
            eps_start - (eps_start - eps_end) * ((ep - 1) / max(1, decay_episodes))
        )

        while not env.game_over:
            state = env.get_state()
            init_state(Q, state)

            action = choose_action(Q, state, epsilon, use_safety=False)
            direction = ACTIONS[action]

            reward, done = env.move(direction, state=state, action=action)

            next_state = env.get_state()
            init_state(Q, next_state)

            update_q(Q, state, action, reward, next_state, alpha, gamma)

            steps += 1
            if done:
                break

        final_len = len(env.snake)
        best_len = max(best_len, final_len)

        if ep % 100 == 0 or ep == episodes:
            print(f"Ep {ep:5d}/{episodes} | len={final_len:2d} | best={best_len:2d} | steps={steps:4d} | eps={epsilon:.3f}")

    save_model(Q, save_path, episodes=episodes)


def evaluate_mode(num_games: int, model_path: str, use_safety: bool = True) -> None:
    """Evaluate the trained model without learning."""
    Q, total_episodes = load_model(model_path)

    epsilon = 0.0
    lengths = []

    print(f"\n{'='*60}")
    print(f"  MODE EVALUATION (dontlearn) - {num_games} parties")
    print(f"{'='*60}")
    print(f"  Model: {model_path}")
    print(f"  Total episodes entraines: {total_episodes}")
    print(f"  Etats dans Q: {len(Q)}")
    print(f"  Epsilon: {epsilon} (exploitation pure)")
    print(f"  Apprentissage: DESACTIVE")
    print(f"  Safety filter: {'ON' if use_safety else 'OFF'}")
    print(f"{'='*60}\n")

    for game in range(1, num_games + 1):
        env = Environment()
        steps = 0

        while not env.game_over:
            state = env.get_state()

            # IMPORTANT : ne pas modifier Q en evaluation
            if state not in Q:
                # action fallback: random (ou safe random si tu veux)
                action = random.randint(0, 3)
            else:
                action = choose_action(Q, state, epsilon, use_safety=use_safety)

            direction = ACTIONS[action]
            _, done = env.move(direction, state=state, action=action)
            steps += 1
            if done:
                break

        final_length = len(env.snake)
        lengths.append(final_length)

        if game % 10 == 0 or game == num_games:
            print(f"Game {game:4d}/{num_games} | length={final_length:2d} | steps={steps:4d}")

    avg_length = sum(lengths) / len(lengths)
    max_length = max(lengths)
    min_length = min(lengths)
    count_10_plus = sum(1 for l in lengths if l >= 10)
    count_5_plus = sum(1 for l in lengths if l >= 5)

    print(f"\n{'='*60}")
    print(f"  RESULTATS EVALUATION")
    print(f"{'='*60}")
    print(f"  Longueur moyenne: {avg_length:.2f}")
    print(f"  Longueur max: {max_length}")
    print(f"  Longueur min: {min_length}")
    print(f"  Parties >=5: {count_5_plus}/{num_games} ({100*count_5_plus/num_games:.1f}%)")
    print(f"  Parties >=10: {count_10_plus}/{num_games} ({100*count_10_plus/num_games:.1f}%)")
    print(f"{'='*60}\n")


def print_vision(env, action_taken: int) -> None:
    """
    Affiche la vision du snake dans le terminal (conforme au sujet).
    """
    vision = env.get_vision_display()
    head_x, head_y = vision["HEAD"]
    
    print("\n" + "="*40)
    print("  SNAKE VISION")
    print("="*40)
    
    # Affichage UP
    print(f"  UP:    {' '.join(vision['UP'])}")
    print(f"  RIGHT: {' '.join(vision['RIGHT'])}")
    print(f"  DOWN:  {' '.join(vision['DOWN'])}")
    print(f"  LEFT:  {' '.join(vision['LEFT'])}")
    print(f"  HEAD:  H (position {head_x},{head_y})")
    print(f"  ACTION: {ACTION_NAMES[action_taken]}")
    print("="*40)


def visual_mode(model_path: str, use_window: bool, fps: int,
                step_by_step: bool = False) -> None:
    """Visualize the trained agent playing."""
    Q, total_episodes = load_model(model_path)

    renderer: Optional[PygameRenderer] = None
    if use_window:
        renderer = PygameRenderer(width=10, height=10, cell_size=50)

    env = Environment()
    epsilon = 0.0
    steps = 0

    print(f"\n{'='*50}")
    print("  MODE VISUALISATION")
    print(f"{'='*50}")
    print(f"  Model: {model_path}")
    print(f"  Total episodes entraines: {total_episodes}")
    print(f"  Etats dans Q: {len(Q)}")
    print(f"  Fenetre: {'ON' if use_window else 'OFF'}")
    if use_window:
        print(f"  FPS: {fps}")
    print(f"  Step-by-step: {'ON' if step_by_step else 'OFF'}")
    if step_by_step:
        print("  (Appuyez sur ENTREE pour avancer)")
    print()

    try:
        while not env.game_over:
            if renderer and not renderer.handle_quit():
                renderer.close()
                return

            if renderer:
                renderer.draw(env.grid, length=len(env.snake), steps=steps, episode=1)
            else:
                display_grid_ascii(env)

            state = env.get_state()
            init_state(Q, state)

            action = choose_action(Q, state, epsilon, use_safety=True)
            direction = ACTIONS[action]

            # Affichage vision + action dans le terminal (conforme au sujet)
            print_vision(env, action)

            # Mode step-by-step
            if step_by_step:
                input("  Appuyez sur ENTREE pour continuer...")

            _, done = env.move(direction, state=state, action=action)
            steps += 1

            if renderer:
                renderer.draw(env.grid, length=len(env.snake), steps=steps, episode=1)
                if not step_by_step:
                    renderer.tick(fps)
            else:
                if not step_by_step:
                    time.sleep(0.15)

            if done:
                break

        # Affichage final
        if renderer:
            renderer.draw(env.grid, length=len(env.snake), steps=steps, episode=1)
            time.sleep(1)
            renderer.close()
        else:
            display_grid_ascii(env)

        print("\n" + "="*50)
        print("  GAME OVER!")
        print(f"  Longueur finale: {len(env.snake)}")
        print(f"  Duree (steps): {steps}")
        print("="*50 + "\n")

    except KeyboardInterrupt:
        if renderer:
            renderer.close()
        print("\n\nVisualisation interrompue.")
