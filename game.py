import pygame


class Checker:

    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color
        self.x = 0
        self.y = 0
        self.calc_position()
        self.king_checker = False

    def calc_position(self):
        # Calculating center of cube for making checker
        self.x = 100 * self.column + 50
        self.y = 100 * self.row + 50

    def make_king_true(self):
        self.king_checker = True

    def draw_checker(self, win):
        pygame.draw.circle(win, "Grey", (self.x, self.y), 42)
        pygame.draw.circle(win, self.color, (self.x, self.y), 40)
        if self.king_checker:
            win.blit(pygame.transform.scale(pygame.image.load('crown.png'), (44, 25)), (
                self.x - (pygame.transform.scale(pygame.image.load("crown.png"), (44, 25))).get_width() // 2,
                self.y - (pygame.transform.scale(pygame.image.load('crown.png'), (44, 25))).get_height() // 2
            ))

    def move(self, row, column):
        self.row = row
        self.column = column
        self.calc_position()


######################################

class Board:

    def __init__(self):
        self.board = []
        self.grey_left = self.white_left = 12
        self.grey_kings = self.white_kings = 0
        self.create_board()

    def draw_cubes(self, win):
        # Create field
        win.fill("Black")
        for row in range(8):
            for column in range(row % 2, 8, 2):
                pygame.draw.rect(win, "White", (row * 100, column * 100, 100, 100))

    def create_board(self):
        # append checkers to list
        for row in range(8):
            self.board.append([])
            for column in range(8):
                if column % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Checker(row, column, "White"))
                    elif row > 4:
                        self.board[row].append(Checker(row, column, "Dimgray"))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw_board(self, win):
        # Draw checkers on field
        self.draw_cubes(win)
        for row in range(8):
            for column in range(8):
                checker = self.board[row][column]
                if checker != 0:
                    # if checker exists
                    checker.draw_checker(win)

    def move(self, checker, row, column):
        # Change list and attribute
        self.board[checker.row][checker.column], self.board[row][column] = self.board[row][column], \
                                                                           self.board[checker.row][checker.column]
        checker.move(row, column)
        if row == 7 or row == 0:
            checker.make_king_true()
            if checker.color == "White":
                self.white_kings += 1
            else:
                self.grey_kings += 1

    def remove(self, checkers):
        # Removing skipped checker
        for checker in checkers:
            self.board[checker.row][checker.column] = 0
            if checker != 0:
                if checker.color == "Dimgray":
                    self.grey_left -= 1
                else:
                    self.white_left -= 1

    def get_valid_moves(self, checker):
        moves = {}
        left = checker.column - 1
        right = checker.column + 1
        row = checker.row

        if checker.color == "Dimgray" or checker.king_checker:
            moves.update(self.traverse_left(row - 1, max(row - 3, -1), -1, checker.color, left))
            moves.update(self.traverse_right(row - 1, max(row - 3, -1), -1, checker.color, right))
            # -1 because Dimgray Checker goes from down to up
        if checker.color == "White" or checker.king_checker:
            moves.update(self.traverse_left(row + 1, min(row + 3, 8), 1, checker.color, left))
            moves.update(self.traverse_right(row + 1, min(row + 3, 8), 1, checker.color, right))
            # +1 because White goes from up to down

        return moves

    def traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                # 2 checkers in a row and we cant beat them
                    break
                elif skipped:
                # 1 checker and after free cube
                    moves[(r, left)] = last + skipped
                else:
                # Free cube
                    moves[(r, left)] = last
                if last:
                # If out of boarders
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, 8)
                    moves.update(self.traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self.traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            left -= 1
        return moves

    def traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= 8:
                break
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, 8)
                    moves.update(self.traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self.traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            right += 1
        return moves

    def winner(self):
        # Find winner
        if self.grey_left <= 0:
            return "Dimgray"
        elif self.white_left <= 0:
            return "White"
        else:
            return None


######################################

class Game:
    def __init__(self, win):
        self.selected_checker = None
        self.board = Board()
        self.turn = "Dimgray"
        self.valid_moves = {}
        self.win = win

    def update_board(self):
        self.board.draw_board(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def select_checker(self, row, column):
        if self.selected_checker:
            # Select a checker and use the move method
            result = self.move(row, column)
            if not result:
                # If the move method returns false, we re-select the checker
                self.selected_checker = None
                self.select_checker(row, column)
        checker = self.board.board[row][column]
        if checker != 0 and checker.color == self.turn:
            self.selected_checker = checker
            self.valid_moves = self.board.get_valid_moves(checker)
            return True
        return False

    def move(self, row, column):
        checker = self.board.board[row][column]
        if self.selected_checker and checker == 0 and (row, column) in self.valid_moves:
            # If the conditions are met, then the checker moves
            self.board.move(self.selected_checker, row, column)
            skipped = self.valid_moves[(row, column)]
            # If we hit a checker, then it is added to the list from which it is then removed.
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == "Dimgray":
            self.turn = "White"
        else:
            self.turn = "Dimgray"

    def draw_valid_moves(self, moves):
        for move in moves:
            row, column = move
            pygame.draw.circle(self.win, "Red", (column * 100 + 100 // 2, row * 100 + 100 // 2), 10)

    def winner(self):
        return self.board.winner()
