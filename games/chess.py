

class Piece:
    def __init__(self, val):
        self.val = val
    def get_black_value(self):
        return -self.val
    def get_white_value(self):
        return  self.val
    def is_move_valid(board):
        assert False, "Not implemented"
    def team(self, piece):
        if piece == 0: return 0
        return piece / abs(piece)
    def append_pseudo_moves(self, board, pos, moves):
        pass

## Most obscure piece with much more rules than the others
## Going two tiles forward, one tile, taking in diagonal and En passant
class Pawn(Piece):
    def is_move_valid(self, board, move):
        start = move.get_start()
        end   = move.get_end()

        x0, y0 = board.to_x_y_coord(start)
        x1, y1 = board.to_x_y_coord(end)

        cur_piece   = board.get(x0, y0)
        ## Should never happen but security check
        piece_color = int(cur_piece / abs(cur_piece)) if cur_piece != 0 else 0

        ## Default MOVE by one
        if board.get(x1, y1) == 0 and x0 == x1 and y0 == y1 - piece_color:
            ## Promotion
            if y1 == 0 or y1 == 7:
                arg = move.args()
                return (len(arg) == 1) and (arg[0] in 'bnrq')
            return True
        ## Default MOVE by two
        if ((y0 == 1 and piece_color == 1) or (y0 == 6 and piece_color == -1)) \
             and board.get(x1, y1 - piece_color) == 0 \
             and board.get(x1, y1) == 0 \
             and y1 - 2 * piece_color == y0:
            return True
        ## DEFAULT TAKE on diagonal
        if (abs(x0 - x1) == 1 and y0 == y1 - piece_color):
            if self.team(board.get(x0, y0)) == -self.team(board.get(x1, y1)):
                return True
        
        ## En passant
        if board.en_passant_row != -1:
            if (abs(x0 - x1) == 1 and y0 == y1 - piece_color):
                if board.get(x1, y0) == -self.val * piece_color:
                    if x1 == board.en_passant_row:
                        return True

        return False
    def append_pseudo_moves(self, board, pos, moves):
        x, y = pos
        piece_color = int(-board.get(x, y) / abs(board.get(x, y)))
        
        if 0 <= y - piece_color <= 7:
            moves.append(Move(0, 'abcdefgh'[x] + str(y + 1) + 'abcdefgh'[x] + str(y - piece_color + 1)))
        if 0 <= y - 2 * piece_color <= 7:
            moves.append(Move(0, 'abcdefgh'[x] + str(y + 1) + 'abcdefgh'[x] + str(y - 2 * piece_color + 1)))
        if 0 <= x + 1 <= 7 and 0 <= y - piece_color <= 7:
            moves.append(Move(0, 'abcdefgh'[x] + str(y + 1) + 'abcdefgh'[x + 1] + str(y - piece_color + 1)))
        if 0 <= x - 1 <= 7 and 0 <= y - piece_color <= 7:
            moves.append(Move(0, 'abcdefgh'[x] + str(y + 1) + 'abcdefgh'[x - 1] + str(y - piece_color + 1)))

## can move anywhere with manhattan distance of one and O-O or O-O-O
class King(Piece):
    def is_move_valid(self, board, move):
        if move.args() != '':
            return False

        start = move.get_start()
        end   = move.get_end()

        x0, y0 = board.to_x_y_coord(start)
        x1, y1 = board.to_x_y_coord(end)

        dx = x1 - x0
        dy = y1 - y0

        if abs(dx) == 2 and dy == 0:
            rook_posx = 7 if dx == 2 else 0
            dxsign = int(dx / abs(dx))

            px = x0 + dxsign
            while px != rook_posx:
                if board.get(px, y0) != 0:
                    return False

                px += dxsign
            
            cboard = board.copy()
            cboard.apply_move (Move(1, move.get_start() + 'abcdefgh'[x0 + dxsign] + str(y0 + 1)))
            
            team = int(self.team(board.get(x0, y0)))

            return (not board.moved[x0][y0]) \
               and (not board.moved[rook_posx][y0]) \
               and (not board.is_check(team)) \
               and (not cboard.is_check(team))

        return max(abs(dx), abs(dy)) == 1 \
            and self.team(board.get(x0, y0)) != self.team(board.get(x1, y1))
    def append_pseudo_moves(self, board, pos, moves):
        x0, y0 = pos
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    if 0 <= x + x0 <= 7 and 0 <= y + y0 <= 7:
                        moves.append(Move(0, 'abcdefgh'[x0] + str(y0 + 1) + 'abcdefgh'[x0 + x] + str(y0 + y + 1)))
## Only rule is diagonal
class Bishop(Piece):
    def is_move_valid(self, board, move):
        if move.args() != '':
            return False

        start = move.get_start()
        end   = move.get_end()

        x0, y0 = board.to_x_y_coord(start)
        x1, y1 = board.to_x_y_coord(end)

        dx = x1 - x0
        dy = y1 - y0

        if dx == 0 or abs(dx) != abs(dy): return False

        for e in range(1, abs(dx)):
            if board.get(x0 + e * int(dx / abs(dx)), y0 + e * int(dy / abs(dy))) != 0:
                return False
        
        return self.team(board.get(x0, y0)) != self.team(board.get(x1, y1))
    def append_pseudo_moves(self, board, pos, moves):
        x0, y0 = pos
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            x = x0+dx
            y = y0+dy
            
            while 0 <= x <= 7 and 0 <= y <= 7:
                moves.append(Move(0, 'abcdefgh'[x0] + str(y0 + 1) + 'abcdefgh'[x] + str(y + 1)))
                if board.get(x, y) != 0:
                    break
                x+=dx
                y+=dy
## Only 'L' shapes
class Knight(Piece):
    def is_move_valid(self, board, move):
        if move.args() != '':
            return False

        start = move.get_start()
        end   = move.get_end()

        x0, y0 = board.to_x_y_coord(start)
        x1, y1 = board.to_x_y_coord(end)

        dx = abs(x0 - x1)
        dy = abs(y0 - y1)

        return ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)) \
            and self.team(board.get(x0, y0)) != self.team(board.get(x1, y1))

    def append_pseudo_moves(self, board, pos, moves):
        x0, y0 = pos
        for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            for nx, ny in [(2, 1), (1, 2)]:
                x = x0 + dx * nx
                y = y0 + dy * ny
                if 0 <= x <= 7 and 0 <= y <= 7:
                    moves.append(Move(0, 'abcdefgh'[x0] + str(y0 + 1) + 'abcdefgh'[x] + str(y + 1)))
## Only rows + cols and O-O + O-O-O
class Rook(Piece):
    def is_move_valid(self, board, move):
        if move.args() != '':
            return False

        start = move.get_start()
        end   = move.get_end()

        x0, y0 = board.to_x_y_coord(start)
        x1, y1 = board.to_x_y_coord(end)

        dx = x1 - x0
        dy = y1 - y0

        if (dx != 0 and dy == 0) or (dx == 0 and dy != 0):
            if dx != 0:
                for x in range(1, abs(dx)):
                    if board.get(x0 + x * int(dx / abs(dx)), y0) != 0:
                        return False
            else:
                for y in range(1, abs(dy)):
                    if board.get(x0, y0 + int(y * dy / abs(dy))) != 0:
                        return False
            return self.team(board.get(x0, y0)) != self.team(board.get(x1, y1))
        return False
    def append_pseudo_moves(self, board, pos, moves):
        x0, y0 = pos
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x = x0+dx
            y = y0+dy
            
            while 0 <= x <= 7 and 0 <= y <= 7:
                moves.append(Move(0, 'abcdefgh'[x0] + str(y0 + 1) + 'abcdefgh'[x] + str(y + 1)))
                if board.get(x, y) != 0:
                    break
                x+=dx
                y+=dy
## rows+cols+diagonals
class Queen(Piece):
    def is_move_valid(self, board, move):
        if move.args() != '':
            return False
        return Bishop(4).is_move_valid(board, move) or Rook(3).is_move_valid(board, move)
    def append_pseudo_moves(self, board, pos, moves):
        Bishop(4).append_pseudo_moves(board, pos, moves)
        Rook(3).append_pseudo_moves(board, pos, moves)

from .models import Move