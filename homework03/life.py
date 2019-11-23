import pathlib

from copy import deepcopy
from random import randint
from typing import List, Optional, Tuple


Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:

    def __init__(
        self,
        size: Tuple[int, int],
        randomize: bool = True,
        max_generations: Optional[float] = float('inf')
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        # Copy from previous assignment
        if randomize:
            return [[randint(0, 1) for i in range(self.cols)]
                    for _ in range(self.rows)]
        else:
            return [[0] * self.cols for _ in range(self.rows)]

    def get_neighbours(self, cell: Cell) -> Cells:
        # Copy from previous assignment
        cells = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                row = cell[0] + i
                col = cell[1] + j
                if i == 0 and j == 0:
                    continue
                elif (row > -1 and row < self.rows and
                      col > -1 and col < self.cols):
                    cells.append(self.curr_generation[row][col])
        return cells

    def get_next_generation(self) -> Grid:
        # Copy from previous assignment
        new_grid = deepcopy(self.curr_generation)
        for row in range(self.rows):
            for col in range(self.cols):
                cell = (row, col)
                alive_neighbours = sum(self.get_neighbours(cell))
                if (alive_neighbours in (2, 3) and
                        self.curr_generation[row][col] == 1):
                    new_grid[row][col] = 1
                elif (alive_neighbours == 3 and
                        self.curr_generation[row][col] == 0):
                    new_grid[row][col] = 1
                else:
                    new_grid[row][col] = 0
        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.prev_generation = deepcopy(self.curr_generation)
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        if self.generations >= self.max_generations:
            return True
        else:
            return False

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        if self.prev_generation == self.curr_generation:
            return False
        else:
            return True

    @staticmethod
    def from_file(filename: pathlib.Path) -> 'GameOfLife':
        """
        Прочитать состояние клеток из указанного файла.
        """
        with open(filename, 'r') as f:
            L = list(f)
            grid = []
            for i in range(len(L)):
                row = []
                for char in L[i]:
                    if char != '\n':
                        row.append(int(char))
                    else:
                        break
                grid.append(row)
        rows = len(grid)
        columns = len(grid[0])
        size = (rows, columns)
        game = GameOfLife(size, True)
        game.curr_generation = grid
        return game

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        with open(filename, 'w') as f:
            for i in range(self.rows):
                for j in range(self.cols):
                    f.write(str(self.curr_generation[i][j]))
                f.write('\n')


if __name__ == '__main__':
    game = GameOfLife.from_file('grid.txt')

