
#####################
# IMPORTS           #
#####################

from django.db                  import models
from django.contrib.auth.models import User
from django.db.models.deletion  import CASCADE
import time

#####################
# CHESS GAME        #
#####################

class ChessGame(models.Model):
    player1  = models.ForeignKey(User, on_delete=CASCADE, related_name="player1")
    player2  = models.ForeignKey(User, on_delete=CASCADE, related_name="player2")

    ## Game info stored in a start char, a list_move char
    start_board = models.CharField(max_length=100)
    ## Used to store time codes and moves
    ## Format ';'.join(moves) where for move in moves move is in type timecode|move
    list_move   = models.TextField()
    start_time  = models.BigIntegerField()

    format = models.CharField(max_length=10)
    over = models.BooleanField(default=False)

    def get_user_to_move(self):
        if self.list_move == '': return self.player1
        return self.player1 if self.list_move.count(';') % 2 == 1 else self.player2
    def get_team_to_move(self):
        if self.list_move == '': return 1
        return 1 if self.list_move.count(';') % 2 == 1 else -1

class Move:
    def __init__(self, time, move):
        self.t = time
        self.m = move
    def __str__(self):
        return f"{self.t}|{self.m}"
    def is_special(self):
        return self.m == "O-O" or self.m == "O-O-O"
    def get_start(self):
        return self.m[0:2]
    def get_end(self):
        return self.m[2:4]
    def args(self):
        return self.m[4:len(self.m)]
    def __str__(self):
        return str(self.t) + '|' + str(self.m)

## Get piece idx : PIECE_IDX_BY_FEN.index(type) - 6
## You can get an opponent piece by doing -piece
PIECE_IDX_BY_FEN = "PKBRQN nqrbkp"

#
# Board build
# Oy-----[
# x
# | -(2, 2)
# | -(3, 2)
# K  -(4, 3)
# |
# |
# ^
# With K the white king
# 

class ChessBoard:
    def __init__(self, fen_pos:str, format:str="3|0", start:int=0):
        self.pos    = [[0 for _ in range(8)] for _ in range(8)]
        self.moved  = [[False for _ in range(8)] for _ in range(8)]
        self.player = 1
        self.set_with_fen_pos(fen_pos)

        ## En passant setup
        ## Store the col (abc...) on which the last two advance pawn happened
        self.en_passant_row = -1

        self.start = start
        self.format = format
        self.moves = []
    def copy(self):
        cb = ChessBoard('')
        for x in range(8):
            for y in range(8):
                cb.pos[x][y] = self.pos[x][y]
                cb.moved[x][y] = self.moved[x][y]
        cb.player = self.player
        cb.en_passant_row = self.en_passant_row
        for move in self.moves:
            cb.moves.append(move)
        return cb
    def set_with_fen_pos(self, fen_pos:str):
        cursor_x = 0
        cursor_y = 0
        cursor   = 0

        while cursor < len(fen_pos):
            if fen_pos[cursor] == '/':
                cursor_x  = 0
                cursor_y += 1
            elif fen_pos[cursor] in '12345678':
                cursor_x += int(fen_pos[cursor])
            else:
                self.pos[cursor_x][cursor_y] = PIECE_IDX_BY_FEN.index(fen_pos[cursor]) - 6
                cursor_x += 1
            cursor += 1
    def can_apply_move(self, move, team):
        chess_board = self.copy()
        chess_board.apply_move(move)
        if chess_board.is_check(team):
            return False

        ## A move is of the form <...><col><row>
        if len(move.m) < 4 and not move.is_special(): return False
        if move.is_special(): return self.can_apply_special_move()

        ## Piece type is the -3 argument if none is provided, the piece moved will be a pawn ('P')
        piece_type = self.get_by_str(move.get_start())
        if piece_type == 0 or piece_type / abs(piece_type) != team: return False

        if abs(piece_type) == 6:
            return Pawn(6).is_move_valid(self, move)
        if abs(piece_type) == 5:
            return King(5).is_move_valid(self, move)
        if abs(piece_type) == 4:
            return Bishop(4).is_move_valid(self, move)
        if abs(piece_type) == 3:
            return Rook(3).is_move_valid(self, move)
        if abs(piece_type) == 2:
            return Queen(2).is_move_valid(self, move)
        if abs(piece_type) == 1:
            return Knight(1).is_move_valid(self, move)

        return False
    def apply_move(self, move):
        self.moves.append(move)
        if move.is_special(): return self.apply_special_move()
        start = move.get_start()
        end   = move.get_end()

        x0, y0 = self.to_x_y_coord(start)
        x1, y1 = self.to_x_y_coord(end)

        self.en_passant_row = -1
        if x0 == x1:
            if abs(y0 - y1) == 2:
                if abs(self.pos[x0][y0]) == PIECE_IDX_BY_FEN.index('p') - 6:
                    self.en_passant_row = x0

        if abs(self.pos[x0][y0]) == 6:
            if abs(x1 - x0) == 1:
                if self.pos[x1][y1] == 0:
                    self.pos[x1][y0] = 0
                    self.moved[x1][y0] = True
        
        ## O-O and O-O-O
        if ( abs(self.pos[x0][y0]) == 5 ) :
            if (abs(x1 - x0) == 2 and abs(y1 - y0) == 0):
                dxsign   = int((x1 - x0) / abs (x1 - x0))
                rook_pos = 0 if dxsign == -1 else 7

                self.pos[x0 + dxsign][y0] = self.pos[rook_pos][y0]
                self.pos[rook_pos][y0] = 0
                print(self.pos)

        self.pos[x1][y1] = self.pos[x0][y0]
        if len(move.args()) == 1:
            self.pos[x1][y1]  = self.pos[x0][y0] / abs(self.pos[x0][y0])
            self.pos[x1][y1] *= PIECE_IDX_BY_FEN.index(move.args()[0]) - 6 ## Because move.args()[0] is in 'bnqr'
        self.pos[x0][y0] = 0

        self.moved[x1][y1] = True
        self.moved[x0][y0] = True

        self.player *= -1
    def get(self, x, y):
        return self.pos[x][y]
    def protected_get(self, x, y):
        if 0 <= x <= 7 and 0 <= y <= 7:
            return self.get(x, y)
        return 0
    def get_by_str(self, s):
        return self.get('abcdefgh'.index(s[0]), int(s[1]) - 1)
    def to_x_y_coord(self, s):
        return ('abcdefgh'.index(s[0]), int(s[1]) - 1)
    def is_check(self, team):
        kx, ky = -2, -2
        for x in range(8):
            for y in range(8):
                if self.pos[x][y] == 5 * team:
                    kx = x
                    ky = y
                    break
        
        ## PAWN CHECK
        if self.protected_get(kx + 1, ky + team) == 6 * -team \
        or self.protected_get(kx - 1, ky + team) == 6 * -team:
            return True
        
        ## ROOK / QUEEN - VERTICAL / HORIZONTAL CHECK
        for dx in [-1, 1]:
            x = kx + dx
            while 0 <= x <= 7:
                piece = self.get(x, ky)
                if piece != 0:
                    if piece == 3 * -team or piece == 2 * -team:
                        return True
                    break
                x += dx
        for dy in [-1, 1]:
            y = ky + dy
            while 0 <= y <= 7:
                piece = self.get(kx, y)
                if piece != 0:
                    if piece == 3 * -team or piece == 2 * -team:
                        return True
                    break
                y += dy
        
        ## BISHOP / QUEEN - DIAGONAL CHECK
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            x = kx + dx
            y = ky + dy
            while 0 <= y <= 7 and 0 <= x <= 7:
                piece = self.get(x, y)
                if piece != 0:
                    if piece == 4 * -team or piece == 2 * -team:
                        return True
                    break
                x += dx
                y += dy
        
        ## KNIGHT CHECK
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            for nx, ny in [(2, 1), (1, 2)]:
                piece = self.protected_get(kx + dx * nx, ky + dy * ny)
                if piece == -team:
                    return True

        ## KING AREA
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    piece = self.protected_get(kx + dx, ky + dy)
                    if piece == 5 * -team:
                        return True

        return False
    def get_pseudo_legal_moves(self, team):
        moves = []
        for x in range(8):
            for y in range(8):
                piece = self.get(x, y)
                if piece != 0 and piece / abs(piece) == team:
                    if abs(piece) == 6:
                        Pawn(6).append_pseudo_moves(self, (x, y), moves)
                    if abs(piece) == 5:
                        King(5).append_pseudo_moves(self, (x, y), moves)
                    if abs(piece) == 4:
                        Bishop(4).append_pseudo_moves(self, (x, y), moves)
                    if abs(piece) == 3:
                        Rook(3).append_pseudo_moves(self, (x, y), moves)
                    if abs(piece) == 2:
                        Queen(2).append_pseudo_moves(self, (x, y), moves)
                    if abs(piece) == 1:
                        Knight(1).append_pseudo_moves(self, (x, y), moves)
        return moves
    def get_legal_moves(self, team):
        moves = []

        for move in self.get_pseudo_legal_moves(team):
            if self.can_apply_move(move, team):
                moves.append(move)
        
        return moves
    def is_stalemate(self, team):
        piece_counts = [0, 0]
        other_than_bak = [False, False]
        for x in range(8):
            for y in range(8):
                if self.pos[x][y] != 0:
                    team = 0 if self.pos[x][y] < 0 else 1
                    piece_counts[team] += 1
                    if not abs(self.pos[x][y]) in [1, 4, 5]:
                        other_than_bak[team] = True
        if piece_counts[0] <= 2 and piece_counts[1] <= 2 and not other_than_bak[0] and not other_than_bak[1]:
            return True

        return len(self.get_legal_moves(team)) == 0 and not self.is_check(team)
    def is_checkmate(self, team):
        return len(self.get_legal_moves(team)) == 0 and self.is_check(team)
    
    def find_times (self):
        time0 = int(self.format.split( '|' )[0]) * 60 * 1000
        time1 = int(self.format.split( '|' )[0]) * 60 * 1000
        print(list(map(str, self.moves)))
        for i in range(0, len(self.moves), 2):
            last_time = int(self.start)
            if (i != 0):       
                last_time = int(self.moves[i - 1].t)
                
            time0 -= int(self.moves[i].t) - last_time
            time0 += int(self.format.split( '|' )[1]) * 1000
            
        for i in range(1, len(self.moves), 2):
            last_time = int(self.moves[i - 1].t)
                
            time1 -= int(self.moves[i].t) - last_time
            time1 += int(self.format.split( '|' )[1]) * 1000
            
        return (time0, time1)
    def find_real_times(self):
        time0, time1 = self.find_times()
        last_time = self.start
        if (len(self.moves) != 0):
            last_time = int(self.moves[-1].t)
        
        if len(self.moves) % 2 == 0:
            return (time0 - ( int(time.time() * 1000) - last_time ), time1)
        return (time0, time1 - ( int(time.time() * 1000) - last_time ))
            
#########################
# ANTI CYCLIC IMPORTS   #
#########################

from games.chess import Bishop, King, Knight, Pawn, Queen, Rook