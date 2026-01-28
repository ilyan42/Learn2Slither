import random
import math


WIDTH = 10
HEIGHT = 10

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

ACTIONS = [UP, DOWN, LEFT, RIGHT]


class Environment:
    UP = UP
    DOWN = DOWN
    LEFT = LEFT
    RIGHT = RIGHT

    def __init__(self):
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

        x = random.randint(2, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        self.snake = [(x, y), (x - 1, y), (x - 2, y)]
        self.game_over = False

        self.green_apples = []
        self.red_apple = None

        self.green_apples = [self.random_empty_cell() for _ in range(2)]
        self.red_apple = self.random_empty_cell()

        self.steps_without_food = 0
        self.max_steps_without_food = 100

        self.update_grid()

    ###########################################
    ########## DISTANCE HELPERS ###############
    ###########################################

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

    ###########################################
    ########## GAME LOGIC #####################
    ###########################################
    
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

    def move(self, direction, state=None, action=None):
        """
        direction: (dx, dy)
        state: le state vision-only AVANT le move (optionnel)
        action: int 0..3 correspondant à (UP, RIGHT, DOWN, LEFT) (optionnel)
        Retourne: (reward, done)
        """
        reward = 0.0

        head_x, head_y = self.snake[0]
        dir_x, dir_y = direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # --- collisions (game over) ---
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            self.game_over = True
            return -100.0, True

        if new_head in self.snake:
            self.game_over = True
            return -100.0, True

        # --- manger green ---
        if new_head in self.green_apples:
            self.green_apples.remove(new_head)
            self.green_apples.append(self.random_empty_cell())
            self.snake.insert(0, new_head)  # grow
            self.steps_without_food = 0
            self.update_grid()
            return 20.0, False

        # --- manger red ---
        if new_head == self.red_apple:
            self.red_apple = self.random_empty_cell()
            self.snake.insert(0, new_head)

            # raccourcir de 1 (au total) : on retire 2 segments car on a "insert"
            self.snake.pop()
            if len(self.snake) > 0:
                self.snake.pop()

            if len(self.snake) == 0:
                self.game_over = True
                return -100.0, True

            self.steps_without_food = 0
            self.update_grid()
            return -20.0, False

        # --- move normal ---
        self.snake.insert(0, new_head)
        self.snake.pop()
        self.steps_without_food += 1

        # petit malus par step (pour éviter tourner en rond)
        reward -= 0.01

        # --- shaping "vision-only" (optionnel mais utile) ---
        # Utilise UNIQUEMENT state[action] = ('G',dist) / ('W',1) etc.
        if state is not None and action is not None:
            info = state[action]  # bucket: (sym, dist)
            if isinstance(info, tuple) and len(info) == 2:
                sym, dist = info

                # danger immédiat
                if sym in ("W", "S") and dist == 1:
                    reward -= 1.0

                # aller dans une direction où une green est visible
                if sym == "G":
                    reward += 0.2
                elif sym == "R":
                    reward -= 0.2

        # anti-boucle si trop longtemps sans manger
        if self.steps_without_food > self.max_steps_without_food:
            self.game_over = True
            return -50.0, True

        self.update_grid()
        return reward, False




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

    def _bucket_distance(self, d: int) -> int:
        """
        Réduit la distance à un bucket pour limiter l'espace d'états.
        1 = très proche (1-2)
        2 = proche (3-4)
        3 = loin (5+)
        """
        if d <= 2:
            return 1
        elif d <= 4:
            return 2
        else:
            return 3

    def look_direction(self, dx, dy):
        """
        Regarde dans une direction et retourne ce qui est visible.
        Conforme au sujet: on voit TOUT jusqu'au mur.
        Retourne: (premier_objet, distance_bucket) où premier_objet est le premier
        élément non-vide (G, R, S, W) rencontré.
        """
        x, y = self.snake[0]
        distance = 0
        
        while True:
            x += dx
            y += dy
            distance += 1
            
            # Mur atteint
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                return ("W", self._bucket_distance(distance))
            
            pos = (x, y)
            
            # Pomme verte
            if pos in self.green_apples:
                return ("G", self._bucket_distance(distance))
            
            # Pomme rouge
            if pos == self.red_apple:
                return ("R", self._bucket_distance(distance))
            
            # Corps du snake
            if pos in self.snake:
                return ("S", self._bucket_distance(distance))
        
        # Ne devrait jamais arriver (on finit toujours par un mur)
        return ("W", self._bucket_distance(distance))

    def get_state(self):
        """
        Retourne l'état vision du snake (4 directions).
        Format: ((symbol, distance_bucket), ...)
        Ordre: UP, RIGHT, DOWN, LEFT
        """
        up = self.look_direction(0, -1)
        right = self.look_direction(1, 0)
        down = self.look_direction(0, 1)
        left = self.look_direction(-1, 0)
        
        return (up, right, down, left)

    def get_vision_display(self):
        """
        Retourne l'affichage de la vision du snake pour le terminal.
        Conforme au sujet: affiche ce que le snake voit dans les 4 directions.
        """
        head_x, head_y = self.snake[0]
        
        # Direction UP
        up_vision = []
        for y in range(head_y - 1, -1, -1):
            up_vision.append(self._cell_symbol(head_x, y))
        up_vision.append("W")  # mur du haut
        
        # Direction DOWN
        down_vision = []
        for y in range(head_y + 1, HEIGHT + 1):
            if y < HEIGHT:
                down_vision.append(self._cell_symbol(head_x, y))
            else:
                down_vision.append("W")
        
        # Direction LEFT
        left_vision = []
        for x in range(head_x - 1, -1, -1):
            left_vision.append(self._cell_symbol(x, head_y))
        left_vision.append("W")  # mur de gauche
        
        # Direction RIGHT
        right_vision = []
        for x in range(head_x + 1, WIDTH + 1):
            if x < WIDTH:
                right_vision.append(self._cell_symbol(x, head_y))
            else:
                right_vision.append("W")
        
        return {
            "UP": up_vision,
            "DOWN": down_vision,
            "LEFT": left_vision,
            "RIGHT": right_vision,
            "HEAD": (head_x, head_y)
        }

