from Board.environment import Environment
import random
import os
import sys
import tty
import termios
import time
import argparse
import pickle

KEY_UP = '\x1b[A'
KEY_DOWN = '\x1b[B'
KEY_RIGHT = '\x1b[C'
KEY_LEFT = '\x1b[D'

ACTIONS = [
    Environment.UP,
    Environment.RIGHT,
    Environment.DOWN,
    Environment.LEFT
]

ACTION_NAMES = ["UP", "RIGHT", "DOWN", "LEFT"]

Q = {}


def save_model(Q, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(Q, f)
    print(f"Modele sauvegarde: {path} ({len(Q)} etats)")


def load_model(path):
    if not os.path.exists(path):
        print(f"Fichier non trouve: {path}")
        return None
    with open(path, "rb") as f:
        Q = pickle.load(f)
    print(f"Modele charge: {path} ({len(Q)} etats)")
    return Q


def init_state(q, state):
    if state not in q:
        q[state] = [0, 0, 0, 0]


def choose_action(Q, state, epsilon):
    if random.random() < epsilon:
        return random.randint(0, 3)
    values = Q[state]
    max_v = max(values)
    best_actions = [i for i, v in enumerate(values) if v == max_v]
    return random.choice(best_actions)


def update_q(Q, state, action, reward, next_state, alpha, gamma):
    best_next = max(Q[next_state])
    Q[state][action] += alpha * (reward + gamma * best_next - Q[state][action])


def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(3)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')


def display_grid_visual(env, show_info=True):
    clear_screen()
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{BOLD}+{'=' * 21}+{RESET}")
    
    for y in range(len(env.grid)):
        print(f"{BOLD}|{RESET}", end=" ")
        for x in range(len(env.grid[0])):
            pos = (x, y)
            if pos == env.snake[0]:
                print(f"{YELLOW}O{RESET}", end=" ")
            elif pos in env.snake:
                print(f"{BLUE}o{RESET}", end=" ")
            elif pos in env.green_apples:
                print(f"{GREEN}G{RESET}", end=" ")
            elif pos == env.red_apple:
                print(f"{RED}R{RESET}", end=" ")
            else:
                print(".", end=" ")
        print(f"{BOLD}|{RESET}")
    
    print(f"{BOLD}+{'=' * 21}+{RESET}")
    
    if show_info:
        print(f"\n{BOLD}Longueur:{RESET} {len(env.snake)}")
        print(f"{BOLD}Etat:{RESET} {env.get_state()}")


def train_mode(episodes=2000, show_stats=True, save_checkpoints=None, model_path=None):
    global Q
    
    alpha = 0.2
    gamma = 0.95
    epsilon_start = 0.4
    epsilon_end = 0.05
    decay_episodes = int(episodes * 0.7)

    best_len = 0
    stats = []
    total_steps = 0
    
    if save_checkpoints is None:
        save_checkpoints = []

    print(f"\n{'='*60}")
    print(f"  MODE ENTRAINEMENT - {episodes} episodes")
    print(f"{'='*60}")
    print(f"  Alpha: {alpha} | Gamma: {gamma}")
    print(f"  Epsilon: {epsilon_start} -> {epsilon_end}")
    if save_checkpoints:
        print(f"  Checkpoints: {save_checkpoints}")
    print(f"{'='*60}\n")

    for ep in range(1, episodes + 1):
        env = Environment()
        steps = 0
        
        epsilon = max(
            epsilon_end,
            epsilon_start - (epsilon_start - epsilon_end) * ((ep - 1) / decay_episodes)
        )

        while not env.game_over:
            state = env.get_state()
            init_state(Q, state)
            action = choose_action(Q, state, epsilon)
            direction = ACTIONS[action]
            reward, done = env.move(direction)
            steps += 1
            total_steps += 1
            next_state = env.get_state()
            init_state(Q, next_state)
            update_q(Q, state, action, reward, next_state, alpha, gamma)
            if done:
                break

        final_length = len(env.snake)
        best_len = max(best_len, final_length)
        stats.append({
            'episode': ep,
            'length': final_length,
            'steps': steps,
            'best': best_len
        })
        
        if ep in save_checkpoints:
            save_model(Q, f"models/{ep}sess.pkl")
        
        if ep % 100 == 0 or ep == episodes:
            avg_len = sum(s['length'] for s in stats[-100:]) / min(100, len(stats))
            print(f"Ep {ep:5d}/{episodes} | len={final_length:2d} | steps={steps:4d} | best={best_len:2d} | avg={avg_len:.1f} | e={epsilon:.3f}")
        elif ep % 10 == 0:
            print(f"Ep {ep:5d}/{episodes} | len={final_length:2d} | steps={steps:4d} | best={best_len:2d}")

    print(f"\n{'='*60}")
    print(f"  ENTRAINEMENT TERMINE")
    print(f"{'='*60}")
    print(f"  Meilleure longueur: {best_len}")
    print(f"  Etats appris: {len(Q)}")
    print(f"  Total steps: {total_steps}")
    
    if model_path:
        save_model(Q, model_path)
    
    if show_stats:
        display_training_stats(stats)
    
    return Q, stats


def evaluate_mode(num_games=100, model_path=None):
    global Q
    
    if model_path:
        loaded_Q = load_model(model_path)
        if loaded_Q:
            Q = loaded_Q
    
    if not Q:
        print("\nLa Q-table est vide! Chargez un modele ou entrainez d'abord.")
        return None
    
    epsilon = 0.0
    results = []
    
    print(f"\n{'='*60}")
    print(f"  MODE EVALUATION (dontlearn) - {num_games} parties")
    print(f"{'='*60}")
    print(f"  Epsilon: {epsilon} (exploitation pure)")
    print(f"  Apprentissage: DESACTIVE")
    print(f"  Etats dans Q: {len(Q)}")
    print(f"{'='*60}\n")

    for game in range(1, num_games + 1):
        env = Environment()
        steps = 0

        while not env.game_over:
            state = env.get_state()
            init_state(Q, state)
            action = choose_action(Q, state, epsilon)
            direction = ACTIONS[action]
            reward, done = env.move(direction)
            steps += 1
            if done:
                break

        final_length = len(env.snake)
        results.append({'game': game, 'length': final_length, 'steps': steps})
        
        if game % 10 == 0 or game == num_games:
            print(f"Game {game:3d}/{num_games} | length={final_length:2d} | steps={steps:4d}")

    lengths = [r['length'] for r in results]
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
    
    return results


def visual_mode(speed=0.2, model_path=None):
    global Q
    
    if model_path:
        loaded_Q = load_model(model_path)
        if loaded_Q:
            Q = loaded_Q
    
    if not Q:
        print("\nLa Q-table est vide! Chargez un modele ou entrainez d'abord.")
        return
    
    print(f"\n{'='*50}")
    print("  MODE VISUALISATION")
    print(f"{'='*50}")
    print(f"  Etats dans Q: {len(Q)}")
    print("  Ctrl+C pour arreter\n")
    time.sleep(2)
    
    env = Environment()
    epsilon = 0
    
    try:
        while not env.game_over:
            display_grid_visual(env)
            state = env.get_state()
            init_state(Q, state)
            action = choose_action(Q, state, epsilon)
            direction = ACTIONS[action]
            print(f"Action: {ACTION_NAMES[action]}")
            reward, done = env.move(direction)
            time.sleep(speed)
            if done:
                break
        
        display_grid_visual(env)
        print("\n" + "="*50)
        print("  GAME OVER!")
        print(f"  Longueur finale: {len(env.snake)}")
        print("="*50 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nVisualisation interrompue.")


def interactive_mode():
    print(f"\n{'='*50}")
    print("  MODE INTERACTIF")
    print(f"{'='*50}")
    print("  Fleches pour bouger, 'q' pour quitter.\n")
    time.sleep(2)
    
    env = Environment()
    
    key_to_action = {
        KEY_UP: Environment.UP,
        KEY_DOWN: Environment.DOWN,
        KEY_LEFT: Environment.LEFT,
        KEY_RIGHT: Environment.RIGHT,
    }
    
    try:
        while not env.game_over:
            display_grid_visual(env)
            print("Fleches pour bouger, 'q' pour quitter")
            key = get_key()
            if key == 'q' or key == '\x03':
                print("\nPartie interrompue.")
                break
            if key in key_to_action:
                direction = key_to_action[key]
                reward, done = env.move(direction)
                if done:
                    break
        
        display_grid_visual(env)
        print("\n" + "="*50)
        print("  GAME OVER!")
        print(f"  Longueur finale: {len(env.snake)}")
        print("="*50 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nPartie interrompue.")


def generate_models(targets=[1, 10, 100], max_episodes=None):
    global Q
    Q = {}
    
    if max_episodes is None:
        max_episodes = max(targets)
    
    alpha = 0.2
    gamma = 0.95
    epsilon_start = 0.4
    epsilon_end = 0.05
    decay_episodes = int(max_episodes * 0.7)
    
    print(f"\n{'='*60}")
    print(f"  GENERATION DES MODELES: {targets}")
    print(f"{'='*60}\n")

    for ep in range(1, max_episodes + 1):
        env = Environment()
        
        epsilon = max(
            epsilon_end,
            epsilon_start - (epsilon_start - epsilon_end) * ((ep - 1) / decay_episodes)
        )

        while not env.game_over:
            state = env.get_state()
            init_state(Q, state)
            action = choose_action(Q, state, epsilon)
            direction = ACTIONS[action]
            reward, done = env.move(direction)
            next_state = env.get_state()
            init_state(Q, next_state)
            update_q(Q, state, action, reward, next_state, alpha, gamma)
            if done:
                break

        if ep in targets:
            save_model(Q, f"models/{ep}sess.pkl")
        
        if ep % 10 == 0 or ep in targets:
            print(f"Episode {ep:5d} | length={len(env.snake):2d} | e={epsilon:.3f}")

    print(f"\n{'='*60}")
    print(f"  MODELES GENERES!")
    print(f"{'='*60}")
    for t in targets:
        print(f"  - models/{t}sess.pkl")
    print()


def display_training_stats(stats):
    print(f"\n{'='*60}")
    print("  STATISTIQUES PAR TRANCHE DE 100 EPISODES")
    print(f"{'='*60}\n")
    
    total_episodes = len(stats)
    chunk_size = 100
    
    print(f"{'Tranche':<15} {'Moy.Len':<12} {'Moy.Steps':<12} {'MaxLen':<10}")
    print("-" * 50)
    
    for i in range(0, total_episodes, chunk_size):
        chunk = stats[i:i + chunk_size]
        if not chunk:
            continue
        avg_length = sum(s['length'] for s in chunk) / len(chunk)
        avg_steps = sum(s['steps'] for s in chunk) / len(chunk)
        max_length = max(s['length'] for s in chunk)
        tranche = f"{i+1}-{min(i+chunk_size, total_episodes)}"
        print(f"{tranche:<15} {avg_length:<12.2f} {avg_steps:<12.2f} {max_length:<10}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Learn2Slither - Snake avec Q-Learning")
    
    parser.add_argument('--train', action='store_true', help="Mode entrainement")
    parser.add_argument('--evaluate', action='store_true', help="Mode evaluation (dontlearn)")
    parser.add_argument('--visual', action='store_true', help="Mode visualisation")
    parser.add_argument('--play', action='store_true', help="Mode interactif")
    parser.add_argument('--generate', action='store_true', help="Generer modeles 1,10,100")
    
    parser.add_argument('--episodes', type=int, default=2000, help="Nb episodes (defaut: 2000)")
    parser.add_argument('--games', type=int, default=100, help="Nb parties evaluation")
    parser.add_argument('--speed', type=float, default=0.15, help="Vitesse visu (defaut: 0.15)")
    parser.add_argument('--checkpoints', type=str, default="", help="Ex: 1,10,100")
    
    parser.add_argument('--save', type=str, default="", help="Sauvegarder modele")
    parser.add_argument('--load', type=str, default="", help="Charger modele")
    
    parser.add_argument('--no-stats', action='store_true', help="Pas de stats")
    
    args = parser.parse_args()
    
    global Q
    
    if args.load:
        loaded_Q = load_model(args.load)
        if loaded_Q:
            Q = loaded_Q
    
    checkpoints = []
    if args.checkpoints:
        checkpoints = [int(x.strip()) for x in args.checkpoints.split(',')]
    
    if not (args.train or args.evaluate or args.visual or args.play or args.generate):
        parser.print_help()
        print("\nChoisissez un mode!")
        return
    
    if args.generate:
        generate_models(targets=[1, 10, 100])
    
    if args.train:
        train_mode(
            episodes=args.episodes,
            show_stats=not args.no_stats,
            save_checkpoints=checkpoints,
            model_path=args.save if args.save else None
        )
    
    if args.evaluate:
        evaluate_mode(num_games=args.games, model_path=args.load if args.load else None)
    
    if args.visual:
        visual_mode(speed=args.speed, model_path=args.load if args.load else None)
    
    if args.play:
        interactive_mode()


if __name__ == "__main__":
    main()
