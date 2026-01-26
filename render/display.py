import pygame

class PygameRenderer:
    def __init__(self, width=10, height=10, cell_size=50, margin=2):
        pygame.init()

        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.margin = margin

        self.font = pygame.font.SysFont(None, 24)
        self.clock = pygame.time.Clock()

        w = width * (cell_size + margin) + margin
        h = height * (cell_size + margin) + margin + 40  # bandeau texte
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Learn2Slither")

    def _color_for_cell(self, v):
        # 0 empty, 1 snake, 2 green, 3 red
        if v == 1:
            return (60, 130, 255)   # bleu
        if v == 2:
            return (60, 200, 60)    # vert
        if v == 3:
            return (220, 60, 60)    # rouge
        return (30, 30, 30)         # fond

    def handle_quit(self):
        # Retourne False si l’utilisateur ferme la fenêtre
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def wait_step(self):
        # Step-by-step: attend une touche (ou quit)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True

    def draw(self, grid, length=0, steps=0, episode=0):
        self.screen.fill((15, 15, 15))

        # Dessin de la grille
        for y in range(self.height):
            for x in range(self.width):
                v = grid[y][x]
                color = self._color_for_cell(v)
                px = self.margin + x * (self.cell_size + self.margin)
                py = self.margin + y * (self.cell_size + self.margin) + 40
                pygame.draw.rect(
                    self.screen,
                    color,
                    (px, py, self.cell_size, self.cell_size),
                    border_radius=4
                )

        # Bandeau texte
        text = f"Episode: {episode} | Steps: {steps} | Length: {length}"
        surf = self.font.render(text, True, (220, 220, 220))
        self.screen.blit(surf, (10, 10))

        pygame.display.flip()

    def tick(self, fps=10):
        self.clock.tick(fps)

    def close(self):
        pygame.quit()