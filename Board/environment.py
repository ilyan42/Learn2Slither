import random



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

        self.update_grid()

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
        print("GAME OVER")
        print("Final length:", len(self.snake))
        self.game_over = True
        
    

    def move(self, direction):

        head_x, head_y = self.snake[0]
        dir_x, dir_y = direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # wall collision
        if not (0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT):
            print("Collision with wall!")
            self.GameOver()
            return False

        if (new_head in self.green_apples):
            self.green_apples.remove(new_head)
            self.green_apples.append(self.random_empty_cell())
            self.snake.insert(0, new_head)
            return True

        if new_head == self.red_apple:
            self.red_apple = self.random_empty_cell()
            self.snake.insert(0, new_head)
            self.snake.pop()
            if len(self.snake) > 0:
                self.snake.pop()
                print("Red apple eaten! Snake length:", len(self.snake))
                if len(self.snake) == 0:
                    print("Snake has no more segments left!")
                    self.GameOver()

            self.update_grid()
            return True

        if new_head in self.snake:
            print("Collision with itself!")
            self.GameOver()
            return False

        self.snake.insert(0, new_head)
        self.snake.pop()
        self.update_grid()
        return True

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

    def look_direction(self, dx, dy):
        vision = []

        x, y = self.snake[0]  # tête
        vision.append("H")

        while True:
            x += dx
            y += dy

            symbol = self._cell_symbol(x, y)
            vision.append(symbol)

            if symbol == "W":
                break

        return vision

    def get_state(self):
        up = self.look_direction(0, -1)
        right = self.look_direction(1, 0)
        down = self.look_direction(0, 1)
        left = self.look_direction(-1, 0)

        return (tuple(up), tuple(right), tuple(down), tuple(left))

