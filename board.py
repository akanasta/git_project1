import pygame


class Board:
    # создание клтчатое поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # значение показывает заполнена клетка спрайтом остановившихся фигур или нет
        # 1 - да, 0 - нет
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left, self.top = 0, 85
        self.cell_size = 40

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        pygame.draw.rect(screen, (210, 70, 70), (300, 10, 80, 40), 2)
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, (41, 7, 15),
                                 (j * self.cell_size + self.left, i * self.cell_size + self.top,
                                  self.cell_size, self.cell_size))
                pygame.draw.rect(screen, (210, 70, 70),
                                 (j * self.cell_size + self.left, i * self.cell_size + self.top,
                                  self.cell_size, self.cell_size), 1)

    def get_cell(self, shape_pos):
        x = (shape_pos[0] - self.left) // self.cell_size
        y = (shape_pos[1] - self.top) // self.cell_size
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None
        return x, y

    def get_stop(self, shape_pos, stay_or_move=True):
        cell = self.get_cell(shape_pos)
        if cell:
           self.on_stop(cell, stay_or_move)

    def on_stop(self, cell_coords, stay_or_move):  # меняет значение в списке для клеток, заполненных спрайтами
        if stay_or_move:
            self.board[cell_coords[1]][cell_coords[0]] = 1
        else:
            self.board[cell_coords[1]][cell_coords[0]] = 0
