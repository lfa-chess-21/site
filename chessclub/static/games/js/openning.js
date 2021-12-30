

(function () {

    let URL = '/static/games/documents/openning_book.eco'

    class Openning {
        constructor ( name, moves ) {



        }
    }

    class PGNBoard {
        constructor () {
            self.board = [
                [1, 2, 3, 4, 5, 3, 2, 1],
                [6] * 8,
                [0] * 8,
                [0] * 8,
                [0] * 8,
                [0] * 8,
                [-6] * 8,
                [-1, -2, -3, -4, -5, -3, -2, -1],
            ]
            self.turn = 1
        }
        to_real_move(move) {
            if (move == 'O-O' || move == 'O-O-O')
                return move

            let end_position = move.substring(move.length - 2, move.length)
            let eaten = move.includes('x')
            let type = 6
            let columns = [0, 1, 2, 3, 4, 5, 6, 7]
            let rows = [0, 1, 2, 3, 4, 5, 6, 7]

            for (let i = 0; i < move.length - 2; i++) {
                if ('RNBKQ'.includes(move[i])) {
                    type = 'RNBKQ'.indexOf(move[i])
                }
                if ('12345678'.includes(move[i])) {
                    columns = ['12345678'.indexOf(move[i])]
                }
                if ('abcdefgh'.includes(move[i])) {
                    rows = ['abcdefgh'.indexOf(move[i])]
                }
            }

            
        }
        apply_move (move) {
            if (move == 'O-O') {

            } else if (move == 'O-O-O') {

            } else {

            }

            self.turn *= -1
        }
    }

})();

