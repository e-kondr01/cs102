import pygame

from copy import deepcopy
from pygame.locals import *
from random import randint
from typing import List, Tuple


Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:

    def __init__(
            self, width: int = 640, height: int = 480,
            cell_size: int = 10, speed: int = 10) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))

    def run(self) -> None:
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))

        # Создание списка клеток
        self.grid = self.create_grid(randomize=True)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            # Отрисовка списка клеток
            self.draw_grid()
            self.draw_lines()
            # Выполнение одного шага игры (обновление состояния ячеек)
            self.grid = self.get_next_generation()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()

    def create_grid(self, randomize: bool = False) -> Grid:
        """
        Создание списка клеток.

        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.

        Parameters
        ----------
        randomize : bool
            Если значение истина, то создается матрица, где каждая клетка может
            быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.

        Returns
        ----------
        out : Grid
            Матрица клеток размером `cell_height` х `cell_width`.
        """
        if randomize:
            return [[randint(0, 1) for i in range(self.cell_width)]
                    for _ in range(self.cell_height)]
        else:
            return [[0] * self.cell_width for _ in range(self.cell_height)]

    def draw_grid(self) -> None:
        """
        Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        """
        for i in range(self.cell_width):
            for j in range(self.cell_height):
                x = self.cell_size * i
                y = self.cell_size * j
                if self.grid[j][i] == 0:
                    pygame.draw.rect(self.screen, pygame.Color('white'),
                                     (x, y, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(self.screen, pygame.Color('green'),
                                     (x, y, self.cell_size, self.cell_size))

    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.

        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.

        Parameters
        ----------
        cell : Cell
            Клетка, для которой необходимо получить список соседей. Клетка
            представлена кортежем, содержащим ее координаты на игровом поле.

        Returns
        ----------
        out : Cells
            Список соседних клеток.
        """
        cells = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                x = cell[1] + i
                y = cell[0] + j
                if i == 0 and j == 0:
                    continue
                elif (x > -1 and x < self.cell_width and
                        y > -1 and y < self.cell_height):
                    cells.append(self.grid[y][x])
        return cells

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.

        Returns
        ----------
        out : Grid
            Новое поколение клеток.
        """
        new_grid = deepcopy(self.grid)
        for y in range(self.cell_height):
            for x in range(self.cell_width):
                cell = (y, x)
                alive_neighbours = sum(self.get_neighbours(cell))
                if alive_neighbours in (2, 3) and self.grid[y][x] == 1:
                    new_grid[y][x] = 1
                elif alive_neighbours == 3 and self.grid[y][x] == 0:
                    new_grid[y][x] = 1
                else:
                    new_grid[y][x] = 0
        return new_grid


if __name__ == '__main__':
    game = GameOfLife(320, 240, 20, 1)
    game.run()
