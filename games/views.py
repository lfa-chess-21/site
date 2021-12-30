
################
# IMPORTS      #
################

from chessclub.views                     import BaseView, BaseRouter
from chessclub.websocket.consumers       import REGISTERED_WS_CONSUMERS, RegisteredWSConsumer
from games.models                        import ChessBoard, ChessGame, Move
from tournaments.models                  import Game, Round

from django.contrib.sessions.models      import Session
from django.contrib.auth.models          import User
from django.shortcuts                    import get_object_or_404
from django.db.models                    import Q

import time

################
# VIEWS        #
################

class GameView(BaseView):
    template_name = 'games/game.html'

    def get_context_data(self):
        default = super().get_context_data()
        self.game_uuid = self.kwargs['game_id']
        self.game = get_object_or_404(ChessGame, pk=self.game_uuid)
        default['game'] = self.game
        return default
    def handle_get_request(self):
        response = super().handle_get_request()

        ## Allow SharedArrayBuffer for WASM multi threading
        response['Cross-Origin-Opener-Policy']   = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'

        return response
    
class AnalysisView(BaseView):
    template_name = 'games/analysis.html'

    def get_context_data(self):
        default = super().get_context_data()
        self.game_uuid = self.kwargs['game_id']
        self.game = get_object_or_404(ChessGame, pk=self.game_uuid)
        default['game'] = self.game
        return default
    def handle_get_request(self):
        response = super().handle_get_request()

        ## Allow SharedArrayBuffer for WASM multi threading
        response['Cross-Origin-Opener-Policy']   = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'

        return response
    

################
# WS VIEWS     #
################

class WSGameView(RegisteredWSConsumer):
    def register_key(self):
        try:
            return self.public_key
        except Exception:
            return -1
    def connect(self):
        self._user    = self.scope['user']
        self.public_key = self.scope['path']
        self.rebuild_key()
        
        self.game_id = int("".join(self.scope['path'].split("/ws/games/")))
        games = ChessGame.objects.filter(id=self.game_id)
        if len(games) != 1:
            self.close()
            return
        self._game = games[0]
        
        key_likes = self.get_key_like()
        if len(key_likes) == 1:
            self._board = ChessBoard(self._game.start_board, self._game.format, self._game.start_time)
            self._board.stalemate_proposition = None
            moves = self._game.list_move.split(";")
            if self._game.list_move != '':
                for move in moves:
                    datas = move.split('|')
                    if len(datas) == 1:
                        datas = [1, datas[0]]
                    self._board.apply_move(Move(int(datas[0]), datas[1]))
        else:
            for _other in key_likes:
                if _other != self:
                    self._board = _other._board
                    self._game  = _other._game
        
        self.accept()

        self.send(f"FEN: {self._game.start_board}/%/FORMAT: {self._game.format}/%/START_TIME: {self._game.start_time}/%/MOVES: {self._game.list_move}")
    def receive(self, text_data=None, bytes_data=None):
        time0, time1 = self._board.find_real_times()

        if time0 <= 0:
            if not self._game.over:
                for consumer in self.get_key_like():
                    consumer.send(f"CHECKMATE: {self._game.player2.username} a gagné par manque de temps")
            self.someone_won(self._game.player2)
        elif time1 <= 0:
            if not self._game.over:
                for consumer in self.get_key_like():
                    consumer.send(f"CHECKMATE: {self._game.player1.username} a gagné par manque de temps")
            self.someone_won(self._game.player1)

        datas = text_data.split(": ")
        
        if datas[0] == "MOVE":
            ## games = ChessGame.objects.filter(id=self.game_id)
            ## if len(games) != 1:
            ##    self.close()
            ##    return
            ## self._game = games[0]
            move = datas[1]
            timestamp = int(time.time() * 1000)

            if self._game.over:
                self.send('INVALID: the game is already over')
                return

            ## TODO make this work
            if self._user != self._game.get_user_to_move():
                self.send("INVALID: it isn't your turn to move or you aren't involved in game")
                return
            
            ## TODO verify move and apply it
            if not self._board.can_apply_move(Move(timestamp, move), self._game.get_team_to_move()):
                self.send(f"INVALID: the move {move} is invalid")
                return
            
            for consumer in self.get_key_like():
                consumer.send(f"MOVE: {timestamp}|{move}")
            
            self._board.apply_move(Move(timestamp, move))
            
            is_checkmate = self._board.is_checkmate(-self._game.get_team_to_move())
            is_stalemate = self._board.is_stalemate(-self._game.get_team_to_move())
            if is_checkmate:
                for consumer in self.get_key_like():
                    consumer.send(f"CHECKMATE: {self._game.get_user_to_move().username} a gagné par échec et mat")
                self.someone_won(self._game.get_user_to_move())

            if is_stalemate:
                for consumer in self.get_key_like():
                    consumer.send(f"STALEMATE: Nulle par pat")
                self.stalemate()

            self._game.list_move = self._game.list_move + (";" if self._game.list_move != "" else "") + str(timestamp) + '|' + move
            self._game.save()

            if self._board.stalemate_proposition == self._game.get_user_to_move():
                self._board.stalemate_proposition = None
        elif datas[0] == "MESSAGE":
            if self._user.is_anonymous:
                return
            
            message = ": ".join(datas[1:len(datas)])

            for consumer in self.get_key_like():
                consumer.send(f"MESSAGE: {self._user.username}: {message}")
        elif datas[0] == "SESSION":
            try:
                self.session_key = datas[1]
                self._session = Session.objects.get(pk=self.session_key)
                session_data = self._session.get_decoded()
                uid = session_data.get('_auth_user_id')
                self._user = User.objects.get(pk=uid)
            except Exception as e:
                pass
        elif datas[0] == "RESIGN":
            if self._user != self._game.player1 \
           and self._user != self._game.player2:
                self.send('INVALID: only one of the players can resign')
                return
            
            if self._game.over:
                self.send('INVALID: you can\'t resign on a game that is over')
                return
            
            if self._user == self._game.player1:
                self.someone_won(self._game.player2)
                for consumer in self.get_key_like():
                    consumer.send(f"CHECKMATE: {self._game.player2.username} a gagné par abandon")
            elif self._user == self._game.player2:
                self.someone_won(self._game.player1)
                for consumer in self.get_key_like():
                    consumer.send(f"CHECKMATE: {self._game.player1.username} a gagné par abandon")
        elif datas[0] == 'STALEMATE':
            if self._user != self._game.player1 \
           and self._user != self._game.player2:
                self.send('INVALID: only one of the players can use stalemate systems')
                return
            
            if self._game.over:
                self.send('INVALID: you can\'t try stalemate on a game that is over')
                return
            other = self._game.player1 if self._game.player2 == self._user else self._game.player2
            
            if datas[1] == 'PROPOSE':
                if self._board.stalemate_proposition == other:
                    self.stalemate()
                    for consumer in self.get_key_like():
                        consumer.send(f"STALEMATE: Nulle par accord mutuel")
                else:
                    for consumer in self.get_key_like():
                        if consumer._user == other:
                            consumer.send(f"STALEMATE: PROPOSE: {self._user.username}")
                    self._board.stalemate_proposition = self._user
            if datas[1] == 'ACCEPT':
                if self._board.stalemate_proposition == other:
                    self.stalemate()
                    for consumer in self.get_key_like():
                        consumer.send(f"STALEMATE: Nulle par accord mutuel")
            if datas[1] == 'REFUSE':
                if self._board.stalemate_proposition == other:
                    self._board.stalemate_proposition = None

        return super().receive(text_data=text_data, bytes_data=bytes_data)
    def stalemate(self):
        self._game.over = True
        self._game.save()
    def someone_won(self, winner):
        if self._game.over:
            return
        self._game.over = True
        self._game.save()

        tournament_games = Game.objects.filter(games=self._game)
        
        for tournament_game in tournament_games:
            if tournament_game.player1 == winner:
                tournament_game.score1 += 1
            else:
                tournament_game.score2 += 1
            tournament_game.save()

            if tournament_game.score1 >= tournament_game.score_needed \
            or tournament_game.score2 >= tournament_game.score_needed:
                won_user = tournament_game.player1 if tournament_game.score1 > tournament_game.score_needed else tournament_game.player2
                rounds = Round.objects.filter( current_game=tournament_game )  
                        
                for round in rounds:
                    upper_rounds = Round.objects.filter (
                        Q (right_has_next=True, right_round=round)
                      | Q ( left_has_next=True,  left_round=round)
                    )
                    for upper_round in upper_rounds:
                        if upper_round.left_round == round \
                        and upper_round.left_has_next:
                            upper_round.current_game.player1 = won_user
                            upper_round.current_game.save()
                        if upper_round.right_round == round \
                        and upper_round.right_has_next:
                            upper_round.current_game.player2 = won_user
                            upper_round.current_game.save()
################
# GAMES ROUTER #
################

class GamesRouter(BaseRouter):
    default_path = 'games/'
    path_array   = [
        ('<int:game_id>', GameView(), 'games.game'),
        ('<int:game_id>/analysis', AnalysisView(), 'games.game.analysis')
    ]

################
# WS ROUTER    #
################

class WebSocketGameRouter(BaseRouter):
    default_path = 'ws/games/'
    path_array   = [
        ('<int:game_id>', WSGameView.as_asgi(), 'ws.games.game_listener')
    ]