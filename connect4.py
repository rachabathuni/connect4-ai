import sys
import random

N_COLUMNS = 7
N_ROWS = 6
TO_WIN = 4

BLANK = 0
PLAYER_1 = 1
PLAYER_2 = 2 
PLAYER_TEXT = ["-", "O", "X"]
PLAYER_TEXT_HIGHLIGHT = ["-", "\033[91mO\033[0m", "\033[91mX\033[0m"]
PLAYER_TEXT_STREAM = ["-", "o", "x"]
PLAYER_TEXT_HIGHLIGHT_STREAM = ["-", "O", "X"]

SUCCESS = 0
ERR_COLUMN_FULL = 1
ERR_INVALID_ROW = 2
ERR_INVALID_COLUMN = 3
ERR_STACK_EMPTY = 4
ERR_NO_MOVES_ALLOWED = 5

MAX_DEPTH = TO_WIN + 2
MIN_WEIGHT = -100000

RANDOMIZE_EQUAL_WEIGHT_MOVES = False

DEBUG = False

def debug(msg):
    if DEBUG:
        sys.stderr.write(msg)
        sys.stderr.write("\n")


class Board:
    def __init__(self):
        self.columns = N_COLUMNS
        self.towin = TO_WIN
        self.rows = N_ROWS
        self.board = []
        self.chips_in_column = [0] * self.columns
        self.move_stack = []
        for i in range(self.rows):
            self.board.append([BLANK] * self.columns)
        self.positive_diag = []
        for i in range(self.rows):
            self.positive_diag.append([None] * self.columns)
        self.negative_diag = []
        for i in range(self.rows):
            self.negative_diag.append([None] * self.columns)
        self._calculate_diags()
        self.next_player = PLAYER_1


    def _calculate_diags(self):
        # Positive
        for i in range(self.columns):
            points = []
            cr = 0
            for j in range(0, min(self.columns-i, self.rows)):
                points.append([cr, i+j])
                cr += 1
            if len(points) >= self.towin:
                for point in points:
                    self.positive_diag[point[0]][point[1]] = points

        for i in range(self.rows):
            points = []
            cc = 0
            for j in range(0, min([self.rows-i, self.columns])):
                points.append([i+j, cc])
                cc += 1
            if len(points) >= self.towin:
                for point in points:
                    self.positive_diag[point[0]][point[1]] = points

        # Negative
        for i in range(self.columns):
            points = []
            cr = 0
            for j in range(0, min([i, self.rows])):
                points.append([cr, i-j])
                cr += 1
            if len(points) >= self.towin:
                for point in points:
                    self.negative_diag[point[0]][point[1]] = points

        for i in range(self.rows):
            points = []
            cc = self.columns-1
            for j in range(0, min([self.rows-i, self.columns])):
                points.append([i+j, cc])
                cc -= 1
            if len(points) >= self.towin:
                for point in points:
                    self.negative_diag[point[0]][point[1]] = points


    def get_columns(self):
        return self.columns


    def get_rows(self):
        return self.rows


    def play(self, column):
        if self.columns <= column:
            return ERR_INVALID_COLUMN

        if self.chips_in_column[column] == self.rows:
            return ERR_COLUMN_FULL

        self.board[self.chips_in_column[column]][column] = self.next_player
        self.chips_in_column[column] += 1
        self.move_stack.append(column)
        self._flip_player()
        return SUCCESS


    def undo(self):
        if len(self.move_stack) == 0:
            return ERR_STACK_EMPTY

        column = self.move_stack.pop(-1)
        self.board[self.chips_in_column[column]-1][column] = BLANK
        self.chips_in_column[column] -= 1
        self._flip_player()
        return SUCCESS


    def _check_column_win(self, player, column):
        return self._check_column_seq(player, column, self.towin)


    def _check_column_seq(self, player, column, target_seq):
        if self.chips_in_column[column] < self.towin:
            return False

        seq = 0
        for i in range(self.chips_in_column[column]):
            if self.board[i][column] == player:
                seq += 1
                if seq == target_seq:
                    return True
            else:
                seq = 0
        return False


    def _check_row_win(self, player, column):
        return self._check_row_seq(player, column, self.towin)


    def _check_row_seq(self, player, column, target_seq):
        seq = 0
        row = self.chips_in_column[column] - 1
        for c in range(self.columns):
            if self.board[row][c] == player:
                seq += 1
                if seq == target_seq:
                    return True
            else:
                seq = 0
        return False


    def _check_one_diag(self, player, diag, row, column, target_seq):
        if diag[row][column]:
            seq = 0
            for point in diag[row][column]:
                if self.board[point[0]][point[1]] == player:
                    seq += 1
                    if seq == target_seq:
                        return True
                else:
                    seq = 0
        return False


    def _check_diag_win(self, player, column):
        return self._check_diag_seq(player, column, self.towin)

    def _check_diag_seq(self, player, column, target_seq):
        row = self.chips_in_column[column]-1
        if self._check_one_diag(player, self.positive_diag, row, column, target_seq):
            return True
        if self._check_one_diag(player, self.negative_diag, row, column, target_seq):
            return True
        return False


    def _flip_player(self):
        self.next_player = PLAYER_2 if self.next_player == PLAYER_1 else PLAYER_1


    def get_last_player(self):
        return PLAYER_2 if self.next_player == PLAYER_1 else PLAYER_1


    def check_win(self):
        player = self.get_last_player()
        if len(self.move_stack) == 0:
            # No moves have been played yet
            return False
        
        column = self.move_stack[-1]
        if self._check_column_win(player, column):
            return True

        if self._check_row_win(player, column):
            return True

        if self._check_diag_win(player, column):
            return True

        return False


    def check_win_in_one(self):
        player = self.get_last_player()
        column = self.move_stack[-1]
        if self._check_column_seq(player, column, self.towin-1):
            return True

        if self._check_row_seq(player, column, self.towin-1):
            return True

        if self._check_diag_seq(player, column, self.towin-1):
            return True

        return False


    def get_chips_in_column(self, column):
        return self.chips_in_column[column]


    def is_column_full(self, column):
        return self.chips_in_column[column] == self.rows


    def is_full(self):
        for c in self.chips_in_column:
            if c < self.rows:
                return False
        return True


    def total_chips(self):
        total = 0
        for c in self.chips_in_column:
            total += c
        return total


    def forward(self, moves):
        ret = None
        for m in moves:
            ret = self.play(m)
            if ret != SUCCESS:
                return ret
            ret = self.check_win()
            if ret:
                ret = ERR_NO_MOVES_ALLOWED
                break
        return ret


    def print_board(self, outstream=sys.stdout):
        last_move = None
        if self.move_stack:
            last_move = [self.chips_in_column[self.move_stack[-1]]-1, self.move_stack[-1]]
        if not DEBUG and outstream == sys.stderr:
            return

        if outstream == sys.stderr:
            player_text_default = PLAYER_TEXT_STREAM
            player_text_highlight = PLAYER_TEXT_HIGHLIGHT_STREAM
        else:
            player_text_default = PLAYER_TEXT
            player_text_highlight = PLAYER_TEXT_HIGHLIGHT

        for r in range(self.rows-1, -1, -1):
            for c in range(len(self.board[r])):
                player_text = player_text_default
                if last_move and \
                        r == last_move[0] and c == last_move[1] and \
                        outstream != sys.stderr:
                    player_text = player_text_highlight
                outstream.write(f"{player_text[self.board[r][c]]} ")
            outstream.write("\n")
        for i in range(self.columns):
            outstream.write(f"{i} ")
        outstream.write("\n")
        outstream.write("======================\n")


class Connect4Engine:
    def __init__(self, board):
        self.board = board

    def _get_best_move(self, cur_depth, max_depth, highest_weight):
        moves = []
        for i in range(self.board.columns):
            if not self.board.is_column_full(i):
                moves.append(i)
        if len(moves) == 0:
            # Board is full
            print("gbm: No moves allowed")
            return ERR_NO_MOVES_ALLOWED, -1, 0

        if RANDOMIZE_EQUAL_WEIGHT_MOVES:
            random.shuffle(moves)

        for move in moves:
            err = self.board.play(move)
            if err != SUCCESS:
                print("Failed to make a move")
                return err, -1, 0

            win = self.board.check_win()
            self.board.undo()
            if win:
                return SUCCESS, move, highest_weight - cur_depth + 1

        if cur_depth == max_depth:
            return SUCCESS, moves[0], 0

        child_max_depth = max_depth
        best_weight = float('inf')
        best_move = None
        for move in moves:
            self.board.play(move)
            e, m, w = self._get_best_move(cur_depth+1, child_max_depth, highest_weight)
            if e == SUCCESS:
                self.board.undo()
            else:
                return e, m, w
            
            if (best_weight == None) or w < best_weight:
                best_weight = w
                best_move = move
                child_max_depth = highest_weight - abs(w) + 1

        return SUCCESS, best_move, best_weight * -1


    def get_best_move(self):
        err, move, weight = self._get_best_move(1, MAX_DEPTH, MAX_DEPTH)
        return err, move


