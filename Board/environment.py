import random
import math


WIDTH = 10
HEIGHT = 10

# Directions as (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

ACTIONS = [UP, DOWN, LEFT, RIGHT]


class Environment:
    # expose directions on the class so callers can use env.UP etc.
    UP = UP
    DOWN = DOWN
    LEFT = LEFT
    RIGHT = RIGHT

    def __init__(self):
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

        # place snake horizontally somewhere that fits at least 3 cells
        x = random.randint(2, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.game_over = False

        self.green_apples = []
        self.red_apple = None

        self.green_apples = [self.random_empty_cell() for _ in range(2)]
        self.red_apple = self.random_empty_cell()

        self.steps_without_food = 0  # Compteur pour éviter les boucles infinies
        self.max_steps_without_food = 100  # Limite de steps sans manger

        self.update_grid()

    def distance_to_nearest_green_apple(self, pos):
        """Calcule la distance Manhattan vers la pomme verte la plus proche."""
        if not self.green_apples:
            return float('inf')
        
        min_dist = float('inf')
        for apple in self.green_apples:
            dist = abs(pos[0] - apple[0]) + abs(pos[1] - apple[1])
            min_dist = min(min_dist, dist)
        return min_dist

    def distance_to_red_apple(self, pos):
        """Calcule la distance Manhattan vers la pomme rouge."""
        if not self.red_apple:
            return float('inf')
        return abs(pos[0] - self.red_apple[0]) + abs(pos[1] - self.red_apple[1])

    def display_grid(self):
        self.update_grid()
        for row in self.grid:
            print(" ".join(str(cell) for cell in row))
    
    def random_empty_cell(self):
        empty = [
            (x, y)
            for y in range(HEIGHT)
            for x in range(WIDTH)
            if (x, y) not in self.snake
            and (x, y) not in self.green_apples
            and (x, y) != self.red_apple
        ]
        return random.choice(empty)

    def GameOver(self):
        self.game_over = True
        
    

    def move(self, direction):
        reward = 0
        done = False

        head_x, head_y = self.snake[0]
        dir_x, dir_y = direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Calcul de la distance avant le mouvement
        old_dist_green = self.distance_to_nearest_green_apple(self.snake[0])
        old_dist_red = self.distance_to_red_apple(self.snake[0])

        # mur = game over
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            reward = -100
            self.GameOver()
            return reward, True

        # collision avec soi-même = game over
        if new_head in self.snake:
            reward = -100
            self.GameOver()
            return reward, True

        # Calcul de la nouvelle distance après mouvement
        new_dist_green = self.distance_to_nearest_green_apple(new_head)
        new_dist_red = self.distance_to_red_apple(new_head)

        # pomme verte
        if new_head in self.green_apples:
            self.green_apples.remove(new_head)
            self.green_apples.append(self.random_empty_cell())
            self.snake.insert(0, new_head)  # grandit
            reward = 20  # Grosse récompense pour manger une pomme verte
            self.steps_without_food = 0  # Reset le compteur
            self.update_grid()
            return reward, False

        # pomme rouge (longueur -1)
        if new_head == self.red_apple:
            self.red_apple = self.random_empty_cell()
            self.snake.insert(0, new_head)
            # pour réduire la longueur de 1 au total :
            self.snake.pop()
            if len(self.snake) > 0:
                self.snake.pop()

            if len(self.snake) == 0:
                reward = -100
                self.GameOver()
                return reward, True

            reward = -10  # Malus pour pomme rouge
            self.steps_without_food = 0
            self.update_grid()
            return reward, False

        # mouvement normal
        self.snake.insert(0, new_head)
        self.snake.pop()
        self.steps_without_food += 1

        # === REWARD SHAPING ===
        
        # Récompense/malus basé sur la distance aux pommes vertes
        if new_dist_green < old_dist_green:
            reward += 1.0  # Se rapproche d'une pomme verte
        elif new_dist_green > old_dist_green:
            reward -= 1.5  # S'éloigne d'une pomme verte (malus plus fort)

        # Malus léger si on se rapproche de la pomme rouge
        if new_dist_red < old_dist_red:
            reward -= 0.3  # Se rapproche de la pomme rouge
        elif new_dist_red > old_dist_red:
            reward += 0.2  # S'éloigne de la pomme rouge

        # Petit malus par step pour encourager l'efficacité
        reward -= 0.05

        # Malus si trop de steps sans manger (évite les boucles)
        if self.steps_without_food > self.max_steps_without_food:
            reward = -50
            self.GameOver()
            return reward, True

        # Bonus de survie progressif basé sur la longueur
        if len(self.snake) >= 5:
            reward += 0.1 * (len(self.snake) - 3)

        self.update_grid()
        return reward, False


    def update_grid(self):
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for x, y in self.snake:
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                self.grid[y][x] = 1
        for x, y in self.green_apples:
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                self.grid[y][x] = 2
        if self.red_apple:
            x, y = self.red_apple
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                self.grid[y][x] = 3

    def _cell_symbol(self, x, y):
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return "W"
        if (x, y) == self.snake[0]:
            return "H"
        if (x, y) in self.snake:
            return "S"
        if (x, y) in self.green_apples:
            return "G"
        if (x, y) == self.red_apple:
            return "R"
        return "0"
    
    def _bucket_distance(self, d):
        if d <= 2:
            return 1
        if d <= 5:
            return 2
        return 3


    def look_bucket(self, dx, dy):
        x, y = self.snake[0]
        steps = 0

        while True:
            x += dx
            y += dy
            steps += 1

            # mur
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                # mur collé
                return ("W", 1) if steps == 1 else ("0", 0)

            pos = (x, y)

            if pos in self.green_apples:
                return ("G", self._bucket_distance(steps))
            if pos == self.red_apple:
                return ("R", self._bucket_distance(steps))
            if pos in self.snake:
                return ("S", self._bucket_distance(steps))


    def get_state(self):
        up = self.look_bucket(0, -1)
        right = self.look_bucket(1, 0)
        down = self.look_bucket(0, 1)
        left = self.look_bucket(-1, 0)

        return (up, right, down, left)

