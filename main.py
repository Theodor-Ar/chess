from math import dist
from fnmatch import fnmatch
from time import time
start_time = time()


class Data:
    """ класс для хранения статистики и прочих данных """


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
    """ клавв для работы с доской """


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
        

    def figure_on_coords(self, x: int, y:int) -> str:
        return self.matrix[7-y][x]


    #  визуальное перемещение фигуры
    def move(self, pos1: tuple, pos2: tuple):
        print(f'moving figure from {pos1} to {pos2}')


class Piece:
    """ общий класс для всех фигур """


    def __init__(self, color):
        self.color = color


    def __call__(self):
        return self.symbol


    def move(self, pos1: tuple, pos2: tuple):
        self.pos1 = pos1
        self.pos2 = pos2

        if self.can_move(pos1, pos2):
            Board.move(pos1, pos2)
        else:
            print(f"This figure can't move from {pos1} to {pos2}")
    

    def friendly_fire(self, x: int, y: int) -> bool:
        if self.color == 'white':
            return Board.figure_on_coords(x, y) in Data.white_pieces
        elif self.color == 'black':
            return Board.figure_on_coords(x, y) in Data.black_pieces
        else:
            raise NameError('Incorrect figure color')


    def empty_cell(self, x: int, y: int) -> bool:
        return Board.figure_on_coords(x, y) == '.'


    def empty_row(self, pos1: tuple, pos2: tuple) -> bool:
        lst = []        
        for x in range(1, 9):
            for y in range(1, 9):
                P = x, y
                if dist(pos1, P) + dist(P, pos2) == dist(pos1, pos2):
                    if pos1 != P != pos2: 
                        lst.append(P)

        return all(self.empty_cell(*i) for i in lst)


    def validate_move(func):
        def wrapper(self, pos1, pos2):
            x1, y1 = pos1
            x2, y2 = pos2

            A = not self.empty_cell(x1, y1)
            B = not self.friendly_fire(x2, y2)

            return A and B and func(self, pos1, pos2)

        return wrapper


class King(Piece):
    """ класс короля """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'K' if color == 'white' else 'k'
            self.value = None

    @Piece.validate_move
    def can_move(self, pos1: tuple, pos2: tuple) -> bool:
        x1, y1 = pos1
        x2, y2 = pos2

        return max(abs(x1 - x2), abs(y1 - y2)) == 1


print(King('white').can_move((4, 0), (5, 1)))


class Queen(Piece):
    """ класс королевы """

    def __init__(self, color):
        super().__init__(color)
        if color in {'black', 'white'}: 
            self.symbol = 'Q' if color == 'white' else 'q'
            self.value = 9

    def can_move(self, pos1: tuple, pos2: tuple) -> bool:
        x1, y1 = pos1
        x2, y2 = pos2

        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        A = dx == dy
        B = dy == 0 != dx
        C = dy != 0 == dx

        return (A or B or C) and Board.empty_row(x2, y2) and Board.end_point(x2, y2)


class Visual:
    """ класс для отображения визуальной части """

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
    """ класс для сборки всей игры """

    def start(self):
        print('game is started')

    def end(self):
        print('game over')



