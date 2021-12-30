
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
        this._fen = fen
        this.played = []
        this.undone = []
    }
    reset () {
        this.array = []
        for (let x = 0; x < 8; x ++) {
            this.array.push([])
            for (let y = 0; y < 8; y ++) {
                this.array[x].push(0)
            }
        }
        this.played = []
        this.undone = []

        this.construct_fen(this._fen)
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

        if (Math.abs(this.array[start[0]][start[1]]) == 6) {
            if (Math.abs(start[0] - end[0]) == 1) {
                if (this.array[end[0]][end[1]] == 0) {
                    this.array[end[0]][start[1]] = 0
                }
            }
        }

        // O-O && O-O-O

        // King at start
        if ( Math.abs(this.array[start[0]][start[1]]) == 5 ) {
            if (Math.abs(start[0] - end[0]) == 2 && Math.abs(start[1] - end[1]) == 0) {
                let dxsign   = (end[0] - start[0]) / Math.abs(start[0] - end[0])
                let rook_pos = dxsign == -1 ? 0 : 7

                this.array[start[0] + dxsign][start[1]] = this.array[rook_pos][start[1]]
                this.array[rook_pos][start[1]] = 0
            }
        }

        this.array[end[0]][end[1]]     = this.array[start[0]][start[1]]
        if (move.m.substring(4, move.m.length).length == 1) {
            this.array[end[0]][end[1]] = this.array[start[0]][start[1]] / Math.abs(this.array[start[0]][start[1]])
            this.array[end[0]][end[1]] *= PIECE_IDX_BY_FEN.indexOf(move.m[4]) - 6
        }
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

    /* undo() {
        let to_undo, piece = this.played[this.played.length - 1]
        this.played.splice(this.played.length - 1)
        this.undone.push(to_undo)

        let move = to_undo
        let start = this.to_x_y_coord(move.get_start())
        let end   = this.to_x_y_coord(move.get_end())

        this.array[end[0]][end[1]]     = this.array[start[0]][start[1]]
        this.array[start[0]][start[1]] = piece
    } */
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

last_mouse_x  = -1;
last_mouse_y  = -1;
last_mouse_dx = -1;
last_mouse_dy = -1;
_onmousemove = function(e){
    e.clientX = e?.pageX ? e.pageX : e.clientX
    e.clientY = e?.pageY ? e.pageY : e.clientY

    last_mouse_dx = e.clientX - last_mouse_x
    last_mouse_dy = e.clientY - last_mouse_y
    last_mouse_x  = e.clientX
    last_mouse_y  = e.clientY

    const drg_area = document.querySelector('#drag-container>img')
    const container = document.querySelector('.gamebox.chessbox.flex-item')

    drg_area.style.left = (last_mouse_x - container.getClientRects()[0].x - drg_area.getClientRects()[0].width  / 2) + 'px'
    drg_area.style.top  = (last_mouse_y - container.getClientRects()[0].y - drg_area.getClientRects()[0].height / 2) + 'px'
}

let DRAG_INFO = null;
let current_container = null;
is_dragging = false;

function start_drag(event) {
    // Set blank image for drag https://stackoverflow.com/questions/38655964/how-to-remove-dragghost-image
    var img = new Image();
    img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=';
    event.dataTransfer.setDragImage(img, 0, 0);

    is_dragging = true;
    DRAG_INFO = event.srcElement

    setTimeout(()=>{DRAG_INFO.style.opacity = '0'}, 0);

    const drg_area = document.querySelector('#drag-container>img')
    drg_area.style.width  = '12.5%'
    drg_area.style.height = '12.5%'
    drg_area.style.pointerEvents = 'none'
    drg_area.src = DRAG_INFO.src
    drg_area.style.opacity = '1'

    document.getElementById('promotion').innerHTML = ''
    document.getElementById('promotion').style.opacity = '0'
    document.getElementById('promotion').style.zIndex = '0'

    document.body.onmousemove = _onmousemove
    document.body.ondragover = _onmousemove
}

function end_drag(event, arg='') {
    let current_container_possibles = document.elementsFromPoint(last_mouse_x, last_mouse_y)
    for (let idx = 0; idx < current_container_possibles.length; idx ++) {
        if (current_container_possibles[idx].classList.contains('chess-piece')) {
            current_container = current_container_possibles[idx]
            break;
        }
    }

    if ((DRAG_INFO.parentNode != current_container && DRAG_INFO != current_container) && (current_container?.classList?.contains("chess-piece") || current_container?.parentNode?.classList?.contains("chess-piece"))) {
        let move_start = DRAG_INFO.parentNode.id.replace("chess-piece-", "")
        let move_end   = (current_container.classList.contains("chess-piece") ? current_container.id : current_container.parentNode.id).replace("chess-piece-", "")
        if (arg == '') {
            if ((move_end[1] == '8' && move_start[1] == '7')
            || (move_end[1] == '1' && move_start[1] == '2')) {
                const drg_area = document.querySelector('#drag-container>img')
                if (drg_area.src.endsWith('/static/media/images/pieces/white_pawn.png')
                || drg_area.src.endsWith('/static/media/images/pieces/black_pawn.png')) {
                    let src = drg_area.src
                    document.getElementById('promotion').innerHTML = `
                        <img src='${src.substring(0, src.length - 8) + 'queen.png'}'  promo='q'>
                        <img src='${src.substring(0, src.length - 8) + 'rook.png'}'   promo='r'>
                        <img src='${src.substring(0, src.length - 8) + 'bishop.png'}' promo='b'>
                        <img src='${src.substring(0, src.length - 8) + 'knight.png'}' promo='n'>
                    `
                    document.getElementById('promotion').style.opacity = '1'

                    let inverted = (move_end[1] == '8' ^ build_mode == 1) == 1
                    console.log(inverted ? 8 - 'abcdefgh'.indexOf(move_start[0]) : 'abcdefgh'.indexOf(move_start[0]))

                    document.getElementById('promotion').style.left = `calc(12.5% * ${inverted ? 8 - 'abcdefgh'.indexOf(move_start[0]) : 'abcdefgh'.indexOf(move_start[0])})`
                    document.getElementById('promotion').style.top = inverted ? '50%' : ''
                    document.getElementById('promotion').style.zIndex = '20'
                    drg_area.style.opacity = '0'
                    DRAG_INFO.style.opacity = '1'
                    document.body.onmousemove = undefined
                    document.body.ondragover = undefined

                    let promotions = document.querySelectorAll('#promotion img')
                    for (let idx = 0; idx < promotions.length; idx ++) {
                        promotions[idx].onclick = (event) => {
                            let target    = event.target
                            let promotion = target.attributes['promo'].value
                            
                            end_drag(event, promotion)
                        }
                    }

                    return ;
                }
            }
        }
        
        document.getElementById('promotion').innerHTML = ''
        document.getElementById('promotion').style.opacity = '0'
        document.getElementById('promotion').style.zIndex = '0'

        if (typeof ws !== 'undefined') {
            ws.send("MOVE: " + move_start + move_end + arg)
        } else {
            let fen0 = undefined
            STOCKFISH_WORKER._external_subsys.onmessage = ({ data }) => {
                if ( data.startsWith('Fen') ) {
                    if (fen0 == undefined) {
                        fen0 = data
                        return ;
                    }

                    if (data != fen0) {
                        board.apply_move(new Move(1 + '|' + move_start + move_end + arg))
                        board.build_html(1)
                        board_updated()
                        cancel_move()
                    } else {
                        cancel_move()
                    }
                }
            }
            setTimeout(cancel_move, 500)

            let moves = board.played.map((x) => x[0].m)
            STOCKFISH_WORKER._external_subsys.postMessage(`position fen ${board._fen} w QKqk moves ${moves.join(' ')}`)
            STOCKFISH_WORKER._external_subsys.postMessage(`d`)
            STOCKFISH_WORKER._external_subsys.postMessage(`position fen ${board._fen} w QKqk moves ${moves.join(' ')} ${move_start + move_end + arg}`)
            STOCKFISH_WORKER._external_subsys.postMessage(`d`)
        }
    } else {
        cancel_move()
    }
    is_dragging = false;
}

function cancel_move (add_err=true) {
    if (DRAG_INFO == null)
        return ;

    const drg_area = document.querySelector('#drag-container>img')
    drg_area.style.width  = '0%'
    drg_area.style.height = '0%'

    setTimeout(() => {DRAG_INFO.style.opacity = '1'
    DRAG_INFO = null;}, 0)
    let stalemate_areas = document.querySelectorAll('#reject')
    for (let i = 0; i < stalemate_areas.length; i++) {
        stalemate_areas[i].innerHTML = `<strong>${other_user}</strong> propose la nulle<br>Vous avez refusé la nulle`
    }
    
    if (add_err) {
        if ((DRAG_INFO.parentNode != current_container && DRAG_INFO != current_container)) {
            if (current_container) {
                // TODO make animation better
                // current_container.classList.add('error')
                setTimeout(()=>{                
                    current_container.classList.remove('error')
                }, 100)
            }
        }
    }
}

function drag_over(e) {
    //console.log(e)
    //if (DRAG_INFO && e.target.parentNode.id != "drag-container")
    //    current_container = e.target
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

setTimeout(()=> {
    document.body.ondragover = _onmousemove
}, 0)
