from math import dist
from fnmatch import fnmatch
from time import time
start_time = time()


class Data:
    """Класс для хранения статистики и прочих данных """
    
    @classmethod
    def square_to_coords(cls, command: str) -> tuple:
        pos1, pos2 = command.split('-')
        x1, y1 = pos1[0], pos1[1]
        x2, y2 = pos2[0], pos2[1]
        return (
            cls.cords[x1], cls.cords[y1]
        ), (
            cls.cords[x2], cls.cords[y2]
        )


    white_pieces = {'K', 'Q', 'B', 'R', 'N', 'P'}
    black_pieces = {'k', 'q', 'b', 'r', 'n', 'p'}

    cnt_moves = 0
    cur_color = 'white'

    cords = {
        '1': 0,
        '2': 1,
        '3': 2,
        '4': 3,
        '5': 4,
        '6': 5,
        '7': 6,
        '8': 7,
        'a': 0,
        'b': 1,
        'c': 2,
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7
        }

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

    def get_piece_color(self, x: int, y: int) -> str:
        symbol = self.get_piece(x, y)
        if symbol == '.': 
            return 'empty'
        return 'white' if symbol in Data.white_pieces else 'black'


class Piece:
    """Общий класс для всех фигур"""


    def __init__(self, color):
        self.color = color


    def capture(self, x: int, y: int) -> None:
            fallen_piece = Board.get_piece(x, y)
            if self.color == 'white':
                Data.dead_black[fallen_piece] += 1
                Data.alive_black[fallen_piece] -= 1
            else:
                Data.dead_white[fallen_piece] += 1
                Data.alive_white[fallen_piece] -= 1
            Board.set_piece(x, y, '.')


    def move_piece(self, start_pos: tuple, end_pos: tuple):     
        color = self.color
        pieces = {
            'k': King(color),
            'q': Queen(color),
            'r': Rook(color),
            'n': Knight(color),
            'b': Bishop(color),
            'p': Pawn(color)
        }

        if self.is_empty_cell(*start_pos): 
            print("A piece cannot move from an empty square")
            pass
        else:
            symbol = Board.get_piece(*start_pos)
            piece = pieces[symbol.lower()]
            can_move, description = piece.can_move(start_pos, end_pos)
            if can_move:
                piece.move_handler(start_pos, end_pos)
                Board.move_piece(start_pos, end_pos)
            else:
                print(f"This figure can't move from {start_pos} to {end_pos}")
                print(description)
            
    
    def move_handler(self, start_pos: tuple, end_pos: tuple) -> None:
        pass

    
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
        return not Piece.is_empty_cell(x, y)
        # if self.color == 'white':
        #     return Board.get_piece(x, y) in Data.white_pieces
        # elif self.color == 'black':
        #     return Board.get_piece(x, y) in Data.black_pieces
        # else:
        #     raise NameError('Incorrect figure color')

    @staticmethod
    def is_empty_cell(x: int, y: int) -> bool:
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
            if Board().get_piece_color(*start_pos) != Data.cur_color:
                return False, 'Сейчас ходит другой цвет'
            
            if not all(0 <= a <= 7 for a in (*start_pos, *end_pos)):  # координаты обеих клеток внутри доски
                return False, 'Позиция вне поля'
            
            if start_pos == end_pos:  # ход не в ту же самую клетку
                return False, 'Нельзя ходить в ту же клетку'
            
            if Piece.is_empty_cell(*start_pos):  # на стартовой клетке стоит фигура именно этого цвета
                return False, 'Стартовая клетка пустая'
            
            if not self.is_valid_target_cell(*end_pos):  # конечная клетка не занята своей фигурой 
                return False, 'На конечной клетке находится своя фигура'
            
            return func(self, start_pos, end_pos)
        
        return wrapper


class King(Piece):
    """Класс короля """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'K' if color == 'white' else 'k'
            self.value = None

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        can_move = max(abs(x1 - x2), abs(y1 - y2)) == 1
        description = None
        
        return can_move, description


class Queen(Piece):
    """Класс королевы """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'Q' if color == 'white' else 'q'
            self.value = 9

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx == dy
        B = dy == 0 != dx
        C = dy != 0 == dx
        D = self.is_empty_line(start_pos, end_pos)

        can_move = (A or B or C) and D
        description = None
        
        return can_move, description


class Rook(Piece):
    """Класс ладьи """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'R' if color == 'white' else 'r'
            self.value = 5

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dy == 0 != dx
        B = dy != 0 == dx
        C = self.is_empty_line(start_pos, end_pos)

        can_move = (A or B) and C
        description = None
        
        return can_move, description


class Knight(Piece):
    """Класс коня"""

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'N' if color == 'white' else 'n'
            self.value = 3

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx + dy == 3
        B = 0 not in {dx, dy}

        can_move = A and B 
        description = None
        
        return can_move, description


class Bishop(Piece):
    """Класс слона"""

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'B' if color == 'white' else 'b'
            self.value = 3

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx == dy
        B = self.is_empty_line(start_pos, end_pos)

        can_move = A and B
        description = None
        
        return can_move, description


class Pawn(Piece):
    """Класс пешки"""

    en_passant_pos: tuple = None

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'P' if color == 'white' else 'p'
            self.value = 1

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = abs(x1 - x2)
        color = self.color

        def short_move():
            return all([
                dx == 0,
                y2 - y1 == (1 if color == 'white' else -1),
                Board.get_piece(*end_pos) == '.'
            ])

        def long_move():
            return all([
                dx == 0,
                y2 - y1 == (2 if color == 'white' else -2),
                Board.get_piece(*end_pos) == '.',
                y1 == (1 if color == 'white' else 6),
                self.is_empty_line(start_pos, end_pos)
            ])

        def capture():
            return all([
                dx == 1,
                y2 - y1 == (1 if color == 'white' else -1),
                Board.get_piece(*end_pos) in (Data.black_pieces if color == 'white' else Data.white_pieces) or 
                end_pos == Pawn.en_passant_pos  # взятие на проходе
            ])

        if short_move():
            if y2 == (7 if color == 'white' else 0):
                return True, 'pawn: end of the board'
            return True, 'pawn: short move'

        elif long_move():
            return True, 'pawn: long move'

        elif capture():
            if y2 == (7 if color == 'white' else 0):
                return True, 'pawn: end of the board'
            return True, 'pawn: capture'

        return False, None
    

    def move_handler(self, start_pos: tuple, end_pos: tuple) -> None:
        x1, y1 = start_pos
        x2, y2 = end_pos
        description = self.can_move(start_pos, end_pos)[1]
        color = self.color

        if description == 'pawn: short move':
            Pawn.en_passant_pos = None
            if description == 'pawn: end of the board':
                ...
        elif description == 'pawn: long move':
            Pawn.en_passant_pos = x1, y1 + (1 if color == 'white' else -1)
        elif description == 'pawn: capture':
            if Pawn.en_passant_pos != None:
                enemy_pos = x2, y2 - (1 if color == 'white' else -1)
                self.capture(*enemy_pos)
            else:
                self.capture(*end_pos)
            if description == 'pawn: end of the board':
                ...
            Pawn.en_passant_pos = None

    def __pawn_chenger(self):
        print(f"Выберете фигуру для замены:\nR N B Q")
        input_data = input(f'enter text: ').replace(' ', '').replace(' ', '').strip().lower()


class Visual:
    """Класс для отображения визуальной части"""

    #  вывод таймера 
    def _timer(self) -> str:
        s = ' ' * 5
        c_time = time() - start_time  # текущее время игры с секундах
        # h, m, s = int(c_time // 3600), int(c_time // 60), c_time % 60  # часы - минуты - секунды игры
        # print(f"Время игры: {h:>4}:{m}:{s:.1}")
        print(f'\n{s}game timer was displayed')

    #  вывод кол-ва сделанных ходов
    def _move_counter(self) -> str:
        s = ' ' * 5
        print(f"{s}Количество ходов: {Data.cnt_moves}")

    #  вывод текущего хода
    def _current_move(self) -> str:
        s = ' ' * 5
        color = 'белые' if Data.cur_color == 'white' else 'чёрные'
        print(f"{s}Сейчас ходят: {color}")

    #  вывод доски на экран
    @staticmethod
    def _show_board(ind=5) -> str:
        s = ' ' * ind
        inf = [
            '/exit - завершить игру',
            '<from> - <to> например a2-a3'
        ]

        print(f'\n{s}    A B C D E F G H    {s}|{s*2}Info bar')
        print(f"{s}  +{'-'*17}+  {s}|")
        for i in range(8):
            print(f"{s}{8-i} | {' '.join(Board.matrix[i])} | {8-i}{s}|{s}{str(i+1) + '.' if i < len(inf) else ''} {inf[i] if i < len(inf) else ''}")
        print(f"{s}  +{'-'*17}+  {s}|")
        print(f'{s}    A B C D E F G H    {s}|\n')


    #  вывод всех элементов
    def visual(self):
        self._timer()
        self._move_counter()
        self._current_move()
        self._show_board()


def command_handler(command: str):
    global run
    if fnmatch(command, '[a-h][1-8]-[a-h][1-8]'): 
        start_pos, end_pos = Data.square_to_coords(command)
        color = Board().get_piece_color(*start_pos)
        piece = Piece(color)
        piece.move_piece(start_pos, end_pos)
    elif command == '/exit': 
        run = False
    else: 
        print("\nnothing\n")
        

run = True
def game():
    start_time = time()
    global run
    while run:
        Visual().visual()
        input_data = input(f'enter text: ').replace(' ', '').replace(' ', '').strip().lower()
        command_handler(input_data)
        Data.cnt_moves += 1
        Data.cur_color = 'white' if Data.cnt_moves % 2 == 0 else 'black'


if __name__ == '__main__':
    game()



