from fnmatch import fnmatch
from time import time
from copy import deepcopy
from art import text2art

start_time = time()


class Data:
    """Класс для хранения статистики и прочих данных"""
    
    @classmethod
    def sq_to_crd(cls, square: str) -> tuple:  # функция перевода шазматной позиции в координату
        sym, num = tuple(square)
        return (
            cls.symbols[sym], cls.numbers[num]
        )
    
    @classmethod
    def crd_to_sq(cls, x: int, y: int) -> str:  # функция перевода координаты в шахматную позицию
        x_to_sym = {v: k for k, v in cls.symbols.items()}
        y_to_num = {v: k for k, v in cls.numbers.items()}
        return x_to_sym[x] + y_to_num[y]
    
    @classmethod
    def score(cls, color: str) -> int:
        white_score = 0  # очки белых
        black_score = 0  # очки черных
        for sym, n in cls.dead.items():
            if sym in cls.black_pieces:
                white_score += cls.pieces_value[sym.lower()] * n
            else:
                black_score += cls.pieces_value[sym.lower()] * n
        return white_score if color == 'white' else black_score
    
    @classmethod
    def pieces_positions(cls, color: str) -> list:
        """Позиции фигур по цвету"""
        positions = []
        for x in range(8):
            for y in range(8):
                symbol = Board.get_piece(x, y)
                if symbol in (cls.white_pieces if color == 'white' else cls.black_pieces):
                    positions.append((x, y))
        return positions
    
    @classmethod
    def king_pos(cls, color: str) -> tuple:
        """Позиция короля по цвету"""
        for pos in cls.pieces_positions(color):
            if Board.get_piece(*pos) == ('K' if color == 'white' else 'k'):
                return pos
            
    @classmethod
    def figures_to_chenge(cls, color: str) -> set:
        """Доступные фигуры для замены пешки в конце поля"""

        if color == 'white':
            return cls.white_pieces - {'K', 'P'}
        elif color == 'black':
            return cls.black_pieces - {'k', 'p'}
        else:
            assert color not in {'white', 'black'}, f'{color=} not in {"white", "black"}'

    @classmethod
    def possible_moves(cls, color: str) -> list:
        """Все возможные ходы для одной из сторон"""

        lst = []
        start_positions = cls.pieces_positions(color)
        for start_pos in start_positions:
            for x in range(8):
                for y in range(8):
                    end_pos = x, y
                    piece = Piece.piece(*start_pos)
                    if piece.can_move(start_pos, end_pos)[0]:
                        lst.append((start_pos, end_pos))
                        
        return lst
    
    @classmethod
    def legal_moves(cls, color: str) -> list:
        """Все возможные ходы одной из сторон, после которых не будет угроз королю"""

        lst = []

        for start_pos, end_pos in cls.possible_moves(color):
            end_sym = Board.get_piece(*end_pos)
            # Двигаем фигуру и проверяем, что потом не будет шаха
            Board.move_piece(start_pos, end_pos)
            if not Game.is_check(color):
                lst.append((start_pos, end_pos))
            # Возвращаем фигуру на место
            Board.move_piece(end_pos, start_pos)
            Board.set_piece(*end_pos, end_sym)
        
        return lst




    
    white_pieces = {'K', 'Q', 'B', 'R', 'N', 'P', 'F', 'I', 'S'}
    black_pieces = {'k', 'q', 'b', 'r', 'n', 'p', 'f', 'i', 's'}

    cnt_moves = 0
    cur_color = 'white'
    
    pieces_value = {
        'k': 0,
        'q': 9,
        'r': 5,
        'n': 3,
        'b': 3,
        'p': 1,
        'f': 1,
        'i': 1,
        's': 1
    }

    symbols = {
        'a': 0,
        'b': 1,
        'c': 2,
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7
    }

    numbers = {
        '1': 0,
        '2': 1,
        '3': 2,
        '4': 3,
        '5': 4,
        '6': 5,
        '7': 6,
        '8': 7
    }

    alive = {
        'P': 8,
        'R': 2,
        'N': 2,
        'B': 2,
        'Q': 1,
        'K': 1,
        'F': 0,
        'I': 0,
        'S': 0,
        'p': 8,
        'r': 2,
        'n': 2,
        'b': 2,
        'q': 1,
        'k': 1,
        'f': 0,
        'i': 0,
        's': 0
    }

    dead = {
        'P': 0,
        'R': 0,
        'N': 0,
        'B': 0,
        'Q': 0,
        'K': 0,
        'F': 0,
        'I': 0,
        'S': 0,
        'p': 0,
        'r': 0,
        'n': 0,
        'b': 0,
        'q': 0,
        'k': 0,
        'f': 0,
        'i': 0,
        's': 0
    }


class Board(Data):
    """Класс для работы с шахматной доской"""

    __saved_data = []

    @classmethod
    def backup(cls, n: int = 1) -> None:
        if -len(cls.__saved_data) <= -n < 0:
            saved_data = cls.__saved_data
            cls.matrix, Data.cnt_moves, Data.alive, Data.dead, Pawn.en_passant_pos = saved_data[-n]
            cls.__saved_data = saved_data[:(-n) + 1]
            Data.cur_color = 'white' if Data.cnt_moves % 2 == 0 else 'black'
        else:
            print('No backup')
        
    @classmethod
    def set_backup(cls) -> None:
        packet = (
            deepcopy(cls.matrix),
            deepcopy(Data.cnt_moves),
            deepcopy(Data.alive),
            deepcopy(Data.dead),
            deepcopy(Pawn.en_passant_pos)
        )
        cls.__saved_data.append(packet)

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

    @classmethod
    def get_piece_color(cls, x: int, y: int) -> str:
        symbol = cls.get_piece(x, y)
        if symbol == '.': 
            return 'empty'
        return 'white' if symbol in Data.white_pieces else 'black'
    

class Piece:
    """Родительский класс для всех фигур"""


    def __init__(self, color):
        self.color = color


    @staticmethod
    def capture(x: int, y: int) -> None:
            fallen_piece = Board.get_piece(x, y)
            Data.dead[fallen_piece] += 1
            Data.alive[fallen_piece] -= 1
            Board.set_piece(x, y, '.')
    

    @staticmethod
    def hint(x: int, y: int) -> list:
        """Подсказка допустимых ходов для фигуры"""

        lst = []
        color = Board.get_piece_color(x, y)
        legal_moves = Data.legal_moves(color)
        for start_pos, end_pos in legal_moves:
            if start_pos == (x, y):
                lst.append(end_pos)

        return lst
    

    @staticmethod
    def under_threat() -> list:
        """Функция подсказки позиций, которые находятся по угрозой, для текущего цвета"""
        
        lst = []

        ally_color = Data.cur_color
        enemy_color = 'white' if ally_color == 'black' else 'black'

        ally_positions = Data.pieces_positions(ally_color)
        enemy_moves = Data.legal_moves(enemy_color)

        for _, end_pos in enemy_moves:
            if end_pos in ally_positions:
                lst.append(end_pos)

        return lst

      
    @classmethod
    def piece(cls, x: int, y: int):
        """Функция для возврата класса фигуры, находящейся на определённой позиции"""

        if not cls.is_empty_cell(x, y):
            color = Board.get_piece_color(x, y)
            symbol = Board.get_piece(x, y)
            pieces = {
                'k': King(color),
                'q': Queen(color),
                'r': Rook(color),
                'n': Knight(color),
                'b': Bishop(color),
                'p': Pawn(color),
                'f': Frog(color),
                'i': Infantry(color),
                's': Star(color)
            }
            return pieces[symbol.lower()]
        else:
            assert False, 'Empty cell'


    def move_piece(self, start_pos: tuple, end_pos: tuple) -> None:
        """Функция для перемещения фигуры"""

        if self.is_empty_cell(*start_pos):
            print('Фигура не может ходить с пустой клетки')
        elif Board.get_piece_color(*start_pos) != Data.cur_color:
            print('Сейчас ходит другой цвет')
        else:
            piece = self.piece(*start_pos)
            can_move, desc = piece.can_move(start_pos, end_pos)

            if not can_move:
                sq1 = Data.crd_to_sq(*start_pos)
                sq2 = Data.crd_to_sq(*end_pos)
                print(f"Данная фигура не может ходить с {sq1} на {sq2}")
                if desc: 
                    print(desc)
                return

            if (start_pos, end_pos) not in Data.legal_moves(Data.cur_color):
                print('Недопустимый ход: после него король останется под шахом')
                return

            Board.set_backup()
            piece.move_handler(start_pos, end_pos)
            Board.move_piece(start_pos, end_pos)
            if isinstance(piece, Pawn) and desc and 'end of the board' in desc:
                piece.pawn_chenger(*end_pos)
            Data.cnt_moves += 1
            Data.cur_color = 'white' if Data.cnt_moves % 2 == 0 else 'black'

            
    
    def move_handler(self, start_pos: tuple, end_pos: tuple) -> None:
        if not Piece.is_empty_cell(*end_pos):
            Piece.capture(*end_pos)
        Pawn.en_passant_pos = None

    
    def is_valid_target_cell(self, x: int, y: int) -> bool:
        if self.color == 'white':
            piece = Board.get_piece(x, y)
            return piece not in Data.white_pieces
        elif self.color == 'black':
            piece = Board.get_piece(x, y)
            return piece not in Data.black_pieces
        else:
            raise NameError('Incorrect figure color')


    @staticmethod
    def is_empty_cell(x: int, y: int) -> bool:
        return Board.get_piece(x, y) == '.'


    def is_empty_line(self, start_pos: tuple, end_pos: tuple) -> bool:
        """Функция проверки, что между двумя позициями все клетки пустые"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        lst = [] 

        for x in range(8):
            for y in range(8):
                if (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1) == 0:  # проверка на то, что точка (x, y) лежит на прямой, соединяющей start_pos и end_pos
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

    was_moved = False

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'K' if color == 'white' else 'k'

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        def castling() -> bool:
            """Функция проверки рокировки"""

            # Проверка, что выбрана корректная конечная точка для хода
            A = x2 in {1, 6}
            B = y2 == 0 if self.color == 'white' else 7
            correct_end_pos = A and B
            
            # Проверка, что король на правильной позиции и не ходил
            king_pos = Data.king_pos(self.color)
            C = king_pos == ((4, 0) if self.color == 'white' else (4, 7))
            D = king_pos == start_pos
            E = self.was_moved == False
            correct_king_pos = C and D and E

            # Проверка, что между королём и ладьёй нет фигур
            rook_pos = x2 + (1 if x2 > x1 else -1), y2
            empty_line = self.is_empty_line(king_pos, rook_pos)

            # Проверка, что ладья не ходила
            rook_was_moved = Rook.was_moved_left if x2 < x1 else Rook.was_moved_right

            return correct_end_pos and correct_king_pos and empty_line and not(rook_was_moved)
        
        if castling():
            return True, 'King: castling'

        can_move = max(abs(x1 - x2), abs(y1 - y2)) == 1
        desc = None
        
        return can_move, desc
    

    def move_handler(self, start_pos: tuple, end_pos: tuple) -> None:
        """Функция-обработчик хода короля"""

        x1, _ = start_pos
        x2, y2 = end_pos
        desc = self.can_move(start_pos, end_pos)[1]

        if desc == 'King: castling':
            # Позиции для перемещения ладьи
            rook_start_pos = x2 + (1 if x2 > x1 else -1), y2
            rook_end_pos = x2 - (1 if x2 > x1 else -1), y2

            # Рокировка
            Board.move_piece(start_pos, end_pos)
            Board.move_piece(rook_start_pos, rook_end_pos)

        elif not Piece.is_empty_cell(*end_pos):
            Piece.capture(*end_pos)

        Pawn.en_passant_pos = None
        King.was_moved = True


class Queen(Piece):
    """Класс королевы """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'Q' if color == 'white' else 'q'

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
        desc = None
        
        return can_move, desc


class Rook(Piece):
    """Класс ладьи """

    was_moved_right = False
    was_moved_left = False

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'R' if color == 'white' else 'r'

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
        desc = None
        
        return can_move, desc
    
    def move_handler(self, start_pos: tuple, end_pos: tuple) -> None:
        """Функция-обработчик хода ладьи"""

        if start_pos in {(0, 0), (0, 7)}:
            self.was_moved_left = True
        elif start_pos in {(7, 0), (7, 7)}:
            self.was_moved_right = True

        if not Piece.is_empty_cell(*end_pos):
            Piece.capture(*end_pos)
        Pawn.en_passant_pos = None


class Knight(Piece):
    """Класс коня"""

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'N' if color == 'white' else 'n'

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx + dy == 3
        B = 0 not in {dx, dy}

        can_move = A and B 
        desc = None
        
        return can_move, desc


class Bishop(Piece):
    """Класс слона"""

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'B' if color == 'white' else 'b'

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx == dy
        B = self.is_empty_line(start_pos, end_pos)

        can_move = A and B
        desc = None
        
        return can_move, desc


class Pawn(Piece):
    """Класс пешки"""

    en_passant_pos: tuple = None

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'P' if color == 'white' else 'p'

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
                return True, 'pawn: capture + end of the board'
            return True, 'pawn: capture'

        return False, None
    

    def move_handler(self, start_pos: tuple, end_pos: tuple) -> None:
        """Функция-обработчик хода пешки"""

        x1, y1 = start_pos
        x2, y2 = end_pos
        desc = self.can_move(start_pos, end_pos)[1]
        color = self.color

        if desc == 'pawn: capture + end of the board':
            self.capture(*end_pos)
            Pawn.en_passant_pos = None
        elif desc == 'pawn: end of the board':
            Pawn.en_passant_pos = None
        elif desc == 'pawn: short move':
            Pawn.en_passant_pos = None
        elif desc == 'pawn: long move':
            Pawn.en_passant_pos = x1, y1 + (1 if color == 'white' else -1)
        elif desc == 'pawn: capture':
            if Pawn.en_passant_pos == end_pos:
                enemy_pos = x2, y2 - (1 if color == 'white' else -1)
                self.capture(*enemy_pos)
            else:
                self.capture(*end_pos)
            Pawn.en_passant_pos = None

    def pawn_chenger(self, x: int, y: int) -> None:
        """Функция замены пешки другую на фигуру"""

        color = self.color
        figures_to_chenge = Data.figures_to_chenge(color)
        text = f"Выберите одну из фигур <{'/'.join(figures_to_chenge)}>: "
        if color == 'white':
            piece_symbol = input(text).strip().upper()
        else:
            piece_symbol = input(text).strip().lower()

        # Замена пешки на фигуру
        if piece_symbol in figures_to_chenge:
            Board.set_piece(x, y, piece_symbol)
            Data.alive[piece_symbol] += 1
        else:
            print('-- Неверная фигура -- ')


class Frog(Piece):
    """Класс первой новой фигуры"""
    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'F' if color == 'white' else 'f'

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        # "прыгает" на 2 клетки в радиусе начальной позиции
        A = dx == 2 and 0 <= dy <= 2
        B = 0 <= dx <= 0 and dy == 2

        can_move = A or B
        desc = None
        
        return can_move, desc
    

class Infantry(Piece):
    """Класс второй новой фигуры"""
    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'I' if color == 'white' else 'i'

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        # ходит в радиусе 1 клетки
        A = 0 <= dx <= 1
        B = 0 <= dy <= 1

        can_move = A and B
        desc = None
        
        return can_move, desc


class Star(Piece):
    """Класс второй новой фигуры"""
    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'I' if color == 'white' else 'i'

    @Piece.validate_move
    def can_move(self, start_pos: tuple, end_pos: tuple) -> tuple:
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        # ходит в радиусе 1 клетки
        A = dx == 2 and dy == 0
        B = dx == 0 and dy == 2
        C = dx == 2 and dy == 2

        can_move = A or B or C
        desc = None
        
        return can_move, desc


class Visual:
    """Класс для отображения визуальной части"""

    @staticmethod
    def print_all_moves(color: str) -> None:
        for i, (start_pos, end_pos) in enumerate(Data.legal_moves(color)):
            sym = Board.get_piece(*start_pos)
            sq1 = Data.crd_to_sq(*start_pos)
            sq2 = Data.crd_to_sq(*end_pos)
            print(f"{i + 1}. {sym} {sq1}-{sq2}")


    @staticmethod
    def status() -> None:
        enemy_color = Data.cur_color
        if Game.is_check(enemy_color):
            print(f"-- Шах {'белым' if enemy_color == 'white' else 'чёрным'} --")


    @staticmethod
    def _line() -> None:
        """Вывод разграничительной линии"""
        print(f"{'- ' * 37}")


    @staticmethod
    def timer() -> None:
        """Вывод игрового таймера"""
        c_time = time() - start_time  # текущее время игры с секундах
        h, m, s = int(c_time // 3600), int(c_time // 60), c_time % 60  # часы - минуты - секунды игры
        print(f"\tВремя игры: {h} ч. {m} мин. {s:.2f} сек.")


    @staticmethod
    def move_counter() -> None:
        """Вывод кол-ва ходов"""
        print(f"\tКоличество ходов: {Data.cnt_moves}")


    @staticmethod
    def game_score() -> None:
        """Вывод очков"""
        white_score = Data.score('white')
        black_score = Data.score('black')
        print(f"\tСчёт белых: {white_score}")
        print(f"\tСчёт чёрных: {black_score}")


    @staticmethod
    def current_move() -> None:
        """Вывод текущего цвета"""
        color = 'белые' if Data.cur_color == 'white' else 'чёрные'
        print(f"\tСейчас ходят: {color}")


    @staticmethod
    def show_play_area() -> None:
        """Вывод игрового пространства"""
        s = ' ' * 5
        inf = [
            '<from> - <to> например a2-a3',
            '/hint <cell> - подсказка хода',
            '/undo <num> - откат ходов',
            '/under_threat - позиции под угрозой',
            '/info - игровая информация',
            '/exit - завершить игру'
        ]

        Visual._line()
        print(f'\n\t    A B C D E F G H    {s}|\t  Tips')
        print(f"\t  +{'-'*17}+  {s}|")
        s = ' ' * 5
        for i in range(8):
            matrix_line = Board.matrix[i]
            line = ' '.join(matrix_line)
            n = 8 - i
            tips = f"{str(i + 1) + '.' if i < len(inf) else ''} {inf[i] if i < len(inf) else ''}"
            print(f"\t{n} | {line} | {n}{s}|\t  {tips}")
        print(f"\t  +{'-'*17}+  {s}|")
        print(f'\t    A B C D E F G H    {s}|\n')
        Visual._line()


    @staticmethod
    def info() -> None:
        print('')
        Visual.timer()
        Visual.move_counter()
        Visual.current_move()
        Visual.game_score()


class Game:
    def __init__(self):
        self.run = True
        self.cur_color = 'white' if Data.cnt_moves % 2 == 0 else 'black'
        self.cnt_moves = Data.cnt_moves

    def start(self) -> None:
        while self.run:
            Visual.show_play_area()
            Visual.status()
            input_data = input('enter text: ').strip().lower()
            self.command_handler(input_data)

            if self.is_checkmate(Data.cur_color) or self.is_stalemate(Data.cur_color):
                self.game_over()


    def stop(self) -> None:
        self.run = False

    def game_over(self) -> None:
        if self.is_checkmate('white'):
            print('-- Белым поставлен мат --')
        elif self.is_checkmate('black'):
            print('-- Чёрным поставлен мат --')
        elif self.is_stalemate('white') or self.is_stalemate('black'):
            print('-- Пат --')

        print('-- Игра окончена --')
        print(text2art('GAME OVER'))
        self.stop()


    def command_handler(self, command: str) -> None:
        """Функция-обработчик команд"""

        def chess_move():
            sq1, sq2 = command.split('-')
            start_pos, end_pos = Data.sq_to_crd(sq1), Data.sq_to_crd(sq2)
            color = Board.get_piece_color(*start_pos)
            piece = Piece(color)
            piece.move_piece(start_pos, end_pos)

        def hint():
            _, square = command.split()
            x, y = Data.sq_to_crd(square)
            hint = Piece.hint(x, y)
            if hint:
                print('\nВозможные ходы')
                for i, pos in enumerate(hint):
                    print(f"{i + 1}. {square}-{Data.crd_to_sq(*pos)}")
            else:
                print('\nДопустимых ходов нет')

        def undo():
            _, num = command.split()
            if num:
                try:
                    num = int(num)
                    Board.backup(num)
                except:
                    print('После команды /backup нужно вводить число')
            else:
                Board.backup()

        def under_threat():
            threat_positions = Piece.under_threat()
            if threat_positions:
                print('Фигуры, находящиеся под угрозой')
                for i, pos in enumerate(threat_positions):
                    symbol = Piece.piece(*pos).symbol
                    square = Data.crd_to_sq(*pos)
                    print(f"{i + 1}. {symbol} на {square}")
            else:
                print('Фигур под угрозой нет')
        
        if fnmatch(command, '[a-h][1-8]-[a-h][1-8]'): 
            chess_move()
        elif command == '/exit': 
            self.stop()
        elif fnmatch(command, '/hint [a-h][1-8]'):
            hint()
        elif fnmatch(command, '/undo *'):
            undo()
        elif command == '/info':
            Visual.info()
        elif command == '/under_threat':
            under_threat()
        else: 
            print("\n-- Nothing --\n")
    

    @staticmethod
    def is_check(color: str) -> bool:
        """Функция проверки на шах"""

        king_pos = Data.king_pos(color)
        enemy_color = 'black' if color == 'white' else 'white'
        enemy_positions = Data.pieces_positions(enemy_color)

        for pos in enemy_positions:
            piece = Piece.piece(*pos)
            if piece.can_move(pos, king_pos)[0]:
                return True

        return False
    

    @staticmethod
    def is_checkmate(color: str) -> bool:
        """Функция проверки на мат"""

        if Game.is_check(color) and not Data.legal_moves(color):
            return True
        return False
    

    @staticmethod
    def is_stalemate(color: str) -> bool:
        """Проверка на пат"""
        
        if not Game.is_check(color) and not Data.legal_moves(color):
            return True
        return False

    
if __name__ == '__main__':
    game = Game()
    game.start()
