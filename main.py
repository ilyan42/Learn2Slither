"""Learn2Slither - Snake game with Q-Learning agent."""

import argparse
import random

from modes.game_modes import (
    train_mode,
    evaluate_mode,
    visual_mode,
)


def main() -> None:
    """Main entry point for Learn2Slither."""
    parser = argparse.ArgumentParser(description="Learn2Slither - Snake avec Q-Learning")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--train", action="store_true", help="Mode entrainement")
    mode.add_argument("--evaluate", action="store_true", help="Mode evaluation (dontlearn)")
    mode.add_argument("--visual", action="store_true", help="Mode visualisation")

    parser.add_argument("--load", type=str, default="", help="Charger modele (eval/visual)")
    parser.add_argument("--save", type=str, default="", help="Sauver modele (train)")
    parser.add_argument("--episodes", type=int, default=2000, help="Nb episodes entrainement")

    parser.add_argument("--games", type=int, default=100, help="Nb parties evaluation")

    parser.add_argument("--window", action="store_true", help="Fenetre pygame")
    parser.add_argument("--fps", type=int, default=10, help="FPS pygame (defaut: 10)")
    parser.add_argument("--step", action="store_true", help="Step-by-step pygame")
    parser.add_argument("--no-safety", action="store_true", help="Desactive safety filter en evaluation")

    args = parser.parse_args()


    if args.train:
        if not args.save:
            print("Erreur: --train demande --save models/xxx.pkl")
            return
        train_mode(episodes=args.episodes, save_path=args.save)
        return

    if args.evaluate:
        if not args.load:
            print("Erreur: --evaluate demande --load models/xxx.pkl")
            return
        evaluate_mode(args.games, args.load, use_safety=(not args.no_safety))
        return

    if args.visual:
        if not args.load:
            print("Erreur: --visual demande --load models/xxx.pkl")
            return
        visual_mode(args.load, use_window=args.window, fps=args.fps,
                    step_by_step=args.step)
        return


if __name__ == "__main__":
    main()
