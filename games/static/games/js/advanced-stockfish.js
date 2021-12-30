

class StockfishWorker {
    constructor() {
        this._stock             = new Worker('/static/games/js/stockfish.js')
        this._variant_evaluator = new Worker('/static/games/js/stockfish.js')
        this._external_subsys   = new Worker('/static/games/js/stockfish.js')
        this.messages           = []
        this._stock.onmessage   = this.onmessage
        this._stock.onerror     = (err) => {console.log( err);}

        let thisObj=this;
        this.variant_stack = [];
        this.message_queue = [];
        this._variant_evaluator.onmessage = ({ data }) => {
            if (data.startsWith ('Final evaluation')) {
                let _eval = data.replace('Final evaluation', '')
                                  .replace('(white side)', '')
                                  .replace('(black side)', '').trim()
                let place = thisObj.variant_stack.splice(0, 1)[0]
                
                let best_moves_by_depth = place[0]
                let callback            = place[1]
                let idx0 = place[2]
                let idx1 = place[3]
                best_moves_by_depth[idx0][idx1].evaluation = _eval
                best_moves_by_depth[idx0][idx1].checkmate = place[4] == '(none)'

                let msg = 'position'
                while (msg.startsWith('position') && thisObj.message_queue.length > 0) {
                    msg = thisObj.message_queue.splice(0, 1)[0];
                    thisObj._variant_evaluator.postMessage(msg)
                }

                if (callback != undefined) {
                    callback(best_moves_by_depth[idx0])
                }
            }
            if (data.startsWith('bestmove')) {
                thisObj.variant_stack[0].push(data.replace('bestmove ', ''))

                let msg = 'position'
                while (msg.startsWith('position') && thisObj.message_queue.length > 0) {
                    msg = thisObj.message_queue.splice(0, 1)[0];
                    thisObj._variant_evaluator.postMessage(msg)
                }
            }
        }
    }
    _put (str) {
        this._stock.postMessage(str)
    }
    _set_option ( name, value ) {
        this._put (`setoption name ${name} value ${value}`)   
    }
    
    set_position ( fen, moves ) {
        this.fen = fen
        this.moves = moves.map((x) => x[0].m)
        this._put(`position fen ${fen} w KQkq - 0 1 moves ${moves.join(' ')}`)
    }
    _get_best_move ( callback, move_count=2, depth=5 ) {
        let best_moves_by_depth = [];
        for (let i = 0; i <= depth; i ++) {
            best_moves_by_depth.push( [] )
        }
        let last_depth_given = -1;

        this._set_option('MultiPV', String(move_count))
        this._stock.onmessage = ({ data }) => {
            let datas = data.split(" ")
            if (datas[0] == 'info') {
                if (datas[1] == 'depth' && !datas.includes('currmove')) {
                    let depth = Number(datas[2]);
                    if (depth < 10)
                        return ;

                    let _variant = datas.slice(datas.indexOf('pv') + 1, datas.length)
                    let multipvid = Number(datas[datas.indexOf('multipv') + 1]) - 1
                    best_moves_by_depth[depth][multipvid] = 
                        new Variant (_variant, 0)
                    
                    this.variant_stack.push( [best_moves_by_depth, undefined, depth, multipvid] )
                    if (best_moves_by_depth[depth].length == move_count && depth >= last_depth_given) {
                        last_depth_given = depth
                        this.variant_stack[this.variant_stack.length - 1][1] = callback
                    }

                    if (this.message_queue.length == 0) {
                        this._variant_evaluator.postMessage(`position fen ${this.fen} w KQkq - 0 1 moves ${this.moves.join(' ')} ${_variant.join(' ')}`)
                        this._variant_evaluator.postMessage('go depth 1')
                        this.message_queue.push('eval')
                    } else {
                        this.message_queue.push(`position fen ${this.fen} w KQkq - 0 1 moves ${this.moves.join(' ')} ${_variant.join(' ')}`)
                        this.message_queue.push('go depth 1')
                        this.message_queue.push('eval')
                    }
                }
            }
        }
        this._stock.postMessage(`go depth ${depth}`)
        
    }

    get_best_move(callback_on_change, move_count=2, depth=1) {
        this._get_best_move(callback_on_change, move_count, depth)
    }
}

class Variant {
    constructor ( moves, evaluation, depth ) {
        this.moves      = moves
        this.evaluation = evaluation
        this.checkmate  = false
    }
}

STOCKFISH_WORKER  = new StockfishWorker()
