
const PIECE_IDX_BY_FEN = "PKBRQN nqrbkp"

const piece_images = [
    '/static/media/images/pieces/black_pawn.png',
    '/static/media/images/pieces/black_king.png',
    '/static/media/images/pieces/black_bishop.png',
    '/static/media/images/pieces/black_rook.png',
    '/static/media/images/pieces/black_queen.png',
    '/static/media/images/pieces/black_knight.png',
    '',
    '/static/media/images/pieces/white_knight.png',
    '/static/media/images/pieces/white_queen.png',
    '/static/media/images/pieces/white_rook.png',
    '/static/media/images/pieces/white_bishop.png',
    '/static/media/images/pieces/white_king.png',
    '/static/media/images/pieces/white_pawn.png',
]

class Board {
    constructor(fen) {
        this.array = []
        for (let x = 0; x < 8; x ++) {
            this.array.push([])
            for (let y = 0; y < 8; y ++) {
                this.array[x].push(0)
            }
        }

        this.construct_fen(fen)
        this.played = []
        this.undone = []
    }
    construct_fen ( fen ) {
        let cursor_x = 0;
        let cursor_y = 0;

        let cursor = 0;

        while (cursor < fen.length) {
            if (fen[cursor] == '/') {
                cursor_x  = 0
                cursor_y += 1   
            } else if ("12345678".indexOf(fen[cursor]) != -1) {
                cursor_x += Number(fen[cursor])
            } else {
                this.array[cursor_x][cursor_y] = PIECE_IDX_BY_FEN.indexOf(fen[cursor]) - 6
                cursor_x += 1
            }

            cursor += 1
        }
    }
    apply_move ( move ) {
        let start = this.to_x_y_coord(move.get_start())
        let end   = this.to_x_y_coord(move.get_end())

        this.played.push([move, this.array[start[0]][start[1]]])

        this.array[end[0]][end[1]]     = this.array[start[0]][start[1]]
        this.array[start[0]][start[1]] = 0
    }
    to_x_y_coord ( str ) {
        return ['abcdefgh'.indexOf(str[0]), Number(str[1]) - 1]
    }

    build_html (team) {
        var start = team == -1 ? 0 : 7
        var last  = team == -1 ? 8 : -1
        var adder = team == -1 ? 1 : -1
        var srt_o = team != -1 ? 0 : 7
        var lst_o = team != -1 ? 8 : -1
        var adr_o = team != -1 ? 1 : -1
        var html  = []
        var mod   = team == -1 ? 1 : 0

        for (var y = start; y != last; y += adder) {
            for (var x = srt_o; x != lst_o; x += adr_o) {
                html.push(`<div class="chess-piece ${(y % 2 == mod) ? "inverted" : 0}" id="chess-piece-${'abcdefgh'[x]}${y + 1}">
                    ${this.array[x][y] == 0 ? '' : `<img dragable="true" src="${piece_images[this.array[x][y] + 6]}">`}
                </div>`)
            }
        }

        document.getElementById("piece-container").innerHTML = html.join("")

        apply_drag_functions()
    }

    undo() {
        let to_undo, piece = this.played[this.played.length - 1]
        this.played.splice(this.played.length - 1)
        this.undone.push(to_undo)

        let move = to_undo
        let start = this.to_x_y_coord(move.get_start())
        let end   = this.to_x_y_coord(move.get_end())

        this.array[end[0]][end[1]]     = this.array[start[0]][start[1]]
        this.array[start[0]][start[1]] = piece
    }
}

class Move {
    constructor (str) {
        this.t = str.split("|")[0]
        this.m = str.split("|")[1]
    }
    get_start() {
        return this.m.substring(0, 2)
    }
    get_end() {
        return this.m.substring(2, 4)
    }
}

// TODOOO replace default transparent drag with full drag

let DRAG_INFO = null;
let current_container = null;

function start_drag(event) {
    DRAG_INFO = event.srcElement

    setTimeout(() => {DRAG_INFO.style.opacity = '0'}, 0)
}

function end_drag(event) {
    if ((DRAG_INFO.parentNode != current_container && DRAG_INFO != current_container) && (current_container.classList.contains("chess-piece") || current_container.parentNode.classList.contains("chess-piece"))) {
        let move_start = DRAG_INFO.parentNode.id.replace("chess-piece-", "")
        let move_end   = (current_container.classList.contains("chess-piece") ? current_container.id : current_container.parentNode.id).replace("chess-piece-", "")
        ws.send(move_start + move_end)
    }
    setTimeout(() => {DRAG_INFO.style.opacity = '1'
    DRAG_INFO = null;}, 100)
}

function drag_over(e) {
    if (DRAG_INFO)
        current_container = e.target
}

function apply_drag_functions() {
    const obj = document.querySelectorAll(".chess-piece>img")

    for (var i = 0; i < obj.length; i++) {
        obj[i].ondragstart = start_drag
        obj[i].ondragend   = end_drag
    }

    const containers = document.querySelectorAll(".chess-piece")

    for (var i = 0; i < containers.length; i++) {
        containers[i].addEventListener('dragover', drag_over)
    }
}
