import pygame
from pygame.locals import *

from life import GameOfLife
from ui import UI


class GUI(UI):

    def __init__(
                 self, life: GameOfLife, cell_size: int = 10,
                 speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed
        self.width = cell_size * self.life.cols
        self.height = cell_size * self.life.rows
        self.screen_size = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.screen_size)

    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))

    def draw_grid(self) -> None:
        """
        Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        """
        for i in range(self.life.cols):
            for j in range(self.life.rows):
                x = self.cell_size * i
                y = self.cell_size * j
                if self.grid[j][i] == 0:
                    pygame.draw.rect(self.screen, pygame.Color('white'),
                                     (x, y, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(self.screen, pygame.Color('green'),
                                     (x, y, self.cell_size, self.cell_size))

    def change_status(self) -> None:
        x, y = pygame.mouse.get_pos()
        row = y // self.cell_size
        col = x // self.cell_size
        self.grid[row][col] = (self.grid[row][col] + 1) % 2

    def run(self) -> None:
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        self.grid = self.life.curr_generation
        running = True
        pause = False
        while (running and self.life.is_changing and
               not self.life.is_max_generations_exceeded):
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYUP and event.key == K_SPACE:
                    pause = not pause
                elif pause and event.type == MOUSEBUTTONDOWN:
                    self.change_status()
            self.draw_grid()
            self.draw_lines()
            if not pause:
                self.life.step()
            self.grid = self.life.curr_generation
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


if __name__ == '__main__':
    life = GameOfLife((24, 24), True, max_generations=50)
    gui = GUI(life, 10, 10)
    gui.run()
