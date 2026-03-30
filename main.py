from math import dist
from fnmatch import fnmatch
from time import time
start_time = time()


class Data:
    """Класс для хранения статистики и прочих данных """


    white_pieces = {'K', 'Q', 'B', 'R', 'N', 'P'}
    black_pieces = {'k', 'q', 'b', 'r', 'n', 'p'}


    alive_white = {
        'P': 8,
        'R': 2,
        'N': 2,
        'B': 2,
        'Q': 1,
        'K': 1
    }
    
    dead_white = {
        'P': 0,
        'R': 0,
        'N': 0,
        'B': 0,
        'Q': 0,
        'K': 0
    }

    alive_black = {
        'p': 8,
        'r': 2,
        'n': 2,
        'b': 2,
        'q': 1,
        'k': 1
    }
    
    dead_black = {
        'p': 0,
        'r': 0,
        'n': 0,
        'b': 0,
        'q': 0,
        'k': 0
    }


class Board(Data):
    """Класс для работы с шахматной доской"""

    #  матрица игрового поля
    matrix = [  
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ]
        

    @classmethod
    def get_piece(cls, x: int, y:int) -> str:
        return cls.matrix[7-y][x]
    

    @classmethod
    def set_piece(cls, x: int, y: int, piece: str) -> None:
        cls.matrix[7-y][x] = piece


    @classmethod
    def move_piece(cls, start_pos: tuple, end_pos: tuple):
        cls.set_piece(*end_pos, cls.get_piece(*start_pos))
        cls.set_piece(*start_pos, '.')
        # print(f'moving figure from {start_pos} to {end_pos}')


class Piece:
    """Общий класс для всех фигур"""


    def __init__(self, color):
        self.color = color


    def move_piece(self, start_pos: tuple, end_pos: tuple):
        if self.can_move(start_pos, end_pos):
            Board.move_piece(start_pos, end_pos)
        else:
            print(f"This figure can't move from {start_pos} to {end_pos}")
    

    def is_valid_target_cell(self, x: int, y: int) -> bool:
        if self.color == 'white':
            piece = Board.get_piece(x, y)
            return piece not in Data.white_pieces
        elif self.color == 'black':
            piece = Board.get_piece(x, y)
            return piece not in Data.black_pieces
        else:
            raise NameError('Incorrect figure color')


    def is_valid_start_cell(self, x: int, y: int) -> bool:
        if self.color == 'white':
            return Board.get_piece(x, y) in Data.white_pieces
        elif self.color == 'black':
            return Board.get_piece(x, y) in Data.black_pieces
        else:
            raise NameError('Incorrect figure color')


    def is_empty_cell(self, x: int, y: int) -> bool:
        return Board.get_piece(x, y) == '.'


    def is_empty_line(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos
        lst = [] 

        for x in range(8):
            for y in range(8):
                if (x - x2) * (y2 - y1) - (y - y1) * (x2 - x1) == 0:  # проверка на то, что точка P лежит на прямой, соединяющей start_pos и end_pos
                    conditions = [
                        (x - x1) * (x - x2) <= 0,
                        (y - y1) * (y - y2) <= 0,
                        start_pos != (x, y) != end_pos
                    ]
                    if all(conditions):  # проверка на то, что точка P лежит между start_pos и end_pos
                        lst.append((x, y))

        return all(self.is_empty_cell(*i) for i in lst)


    def validate_move(func):
        def wrapper(self, start_pos, end_pos):
            x1, y1 = start_pos
            x2, y2 = end_pos

            basic_conditions = [
                self.is_valid_target_cell(x2, y2),  # конечная клетка не занята своей фигурой 
                all(0 <= a <= 7 for a in (x1, y1, x2, y2)),  # координаты обеих клеток внутри доски
                self.is_valid_start_cell(x1, y1),  # на стартовой клетке стоит фигура именно этого цвета
                start_pos != end_pos  # ход не в ту же самую клетку
            ]

            return all(basic_conditions) and func(self, start_pos, end_pos)
        return wrapper


class King(Piece):
    """Класс короля """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'K' if color == 'white' else 'k'
            self.value = None

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos

        return max(abs(x1 - x2), abs(y1 - y2)) == 1


class Queen(Piece):
    """Класс королевы """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'Q' if color == 'white' else 'q'
            self.value = 9

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx == dy
        B = dy == 0 != dx
        C = dy != 0 == dx
        D = self.is_empty_line(start_pos, end_pos)

        return (A or B or C) and D


class Rook(Piece):
    """Класс ладьи """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'R' if color == 'white' else 'r'
            self.value = 5

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dy == 0 != dx
        B = dy != 0 == dx
        C = self.is_empty_line(start_pos, end_pos)

        return (A or B) and C


class Knight(Piece):
    """Класс коня"""

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'N' if color == 'white' else 'n'
            self.value = 3

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx + dy == 3
        B = 0 not in {dx, dy}

        return A and B


class Bishop(Piece):
    """Класс слона"""

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'B' if color == 'white' else 'b'
            self.value = 3

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx == dy
        B =self.is_empty_line(start_pos, end_pos)

        return A and B


class Pawn(Piece):
    """Класс пешки"""

    en_passant_pos: tuple = None

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'P' if color == 'white' else 'p'
            self.value = 1

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)

        def short_move():
            conditions = [
                dx == 0,
                y2 - y1 == (1 if self.color == 'white' else -1),
                Board.get_piece(*end_pos) == '.'
            ]
            return all(conditions)

        def long_move():
            conditions = [
                dx == 0, 
                y2 - y1 == (2 if self.color == 'white' else -2), 
                Board.get_piece(*end_pos) == '.', 
                y1 == (1 if self.color == 'white' else 6),
                self.is_empty_line(start_pos, end_pos)
            ]
            return all(conditions)
        
        def capture():
            conditions = [
                dx == 1,
                y2 - y1 == (1 if self.color == 'white' else -1),
                Board.get_piece(*end_pos) in (Data.black_pieces if self.color == 'white' else Data.white_pieces)
            ]
            return all(conditions)
        
        def en_passant_capture():
            conditions = [
                y1 == (3 if self.color == 'white' else 4),  #  пешка на 4-ой или 5-ой линии
                capture(),
                end_pos == self.en_passant_pos
            ]
            return all(conditions)

        return any([
            short_move(), 
            long_move(), 
            capture(), 
            en_passant_capture()
        ])

        # if short_move():
        #     if end_of_board():
        #         pass
        #     else:
        #         Piece.move_piece(start_pos, end_pos)

        # if long_move():
        #     self.en_passant_pos = x1, y1 + (1 if self.color == 'white' else -1)
        #     Piece.move_piece(start_pos, end_pos)

        # return dy == 0 and dx == 1


class Visual:
    """Класс для отображения визуальной части"""

    #  вывод таймера 
    def timer(self) -> str:
        print('game timer was displayed')

    #  вывод кол-ва сделанных ходов
    def move_counter(self) -> str:
        print('number of moves made was displayed')

    #  вывод текущего хода
    def current_move(self) -> str:
        print('current move was dusplayed')

    #  вывод доски на экран
    @staticmethod
    def show_board(ind=5) -> str:

        print(f'\n{' ' * ind}   A B C D E F G H\n')
        for i in range(8):
            print(f"{' ' * ind}{8-i}  {' '.join(Board.matrix[i])}  {8-i}")
        print(f'\n{' ' * ind}   A B C D E F G H\n')


    # def input_data(self):
    #     motion = input('enter text: ').replace(' ', '').lower()
    #     if fnmatch('[a-h][1-8]', motion)
    #     self.motion = motion


    #  вывод всех элементов
    def visual(self):
        self.timer()
        self.move_counter()
        self.current_move()
        self.show_board()


class Game:
    """Класс для сборки всей игры"""

    def start(self):
        print('game is started')

    def end(self):
        print('game over')



