
######################
# IMPORTS            #
######################

from chessclub.views import BaseView, BaseRouter
from chessclub.websocket.consumers import RegisteredWSConsumer
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models import Q
from games.models import ChessGame
from tournaments.models import Tournament, Game, Round
import json
import time
import random

######################
# VIEWS              #
######################

class SocialHomeView(BaseView):
    template_name = "social/index.html"
    
    def handle_get_request(self):
        if self.request.user.is_anonymous:
            return redirect('/account/login?next=/social/')

        return super().handle_get_request()
    def get_context_data(self):
        ctx = super().get_context_data()

        ctx['rounds'] = []

        tournaments = Tournament.objects.filter( players=self.request.user )
        for tournament in tournaments:
            rounds_involved = Round.objects.filter(Q(current_game__player1=self.request.user) | Q(current_game__player2=self.request.user), tournament=tournament)
            for round in rounds_involved:
                if self.playable(round):
                    ctx['rounds'].append(round)
            
        return ctx

    def playable (self, round):
        if round.left_has_next:
            if  round.left_round.current_game.score1 < round.left_round.current_game.score_needed \
            and round.left_round.current_game.score2 < round.left_round.current_game.score_needed:
                return False
        if round.right_has_next:
            if  round.right_round.current_game.score1 < round.right_round.current_game.score_needed \
            and round.right_round.current_game.score2 < round.right_round.current_game.score_needed:
                return False

        return round.current_game.score1 < round.current_game.score_needed \
           and round.current_game.score2 < round.current_game.score_needed
    

######################
# WEBSOCKET VIEWS    #
######################

class WSSocialView(RegisteredWSConsumer):
    def connect(self):
        self._user    = self.scope['user']
        
        if self._user.is_authenticated:
            self.accept()
        self._invit = None
        self.rebuild_key()
    def register_key(self):
        if '_user' in self.__dir__():
            return self._user.username
        return None
    def receive(self, text_data=None, bytes_data=None):
        datas = text_data.split(": ")

        if datas[0] == 'GETDEFAULT':
            messages = Message.objects.filter(Q(author=self._user) | Q(receiver=self._user)).order_by('-pk')[:50]
            
            user_set = set()
            users = []
            for message in messages:
                _other = message.receiver if message.author == self._user else message.author
                if not _other in user_set:
                    user_set.add(_other)
                    users.append([_other.username, message.message])
            self.send('MESSAGES: ' + json.dumps(users))
        
        if datas[0] == 'GET_MESSAGES':
            if len(datas) != 2:
                return
            
            _other = None
            try:
                _other = get_object_or_404(User, username=datas[1])
            except Exception:
                self.send('USERERROR: '+datas[1])
                return
            messages = Message.objects.filter(Q(author=self._user, receiver=_other) | Q(author=_other, receiver=self._user)).order_by('-pk')[:50]
            
            message_arr = [
                [
                    message.author.username,
                    message.message
                ]
                for message in messages
            ]
            self.send("USER_MESSAGES: " + datas[1] + ": " + json.dumps(message_arr))

        if datas[0] == 'MESSAGE':
            user_from = self._user
            usernm_to   = datas[1]
            msg = ': '.join(datas[2:])

            message = f'MESSAGE: {user_from.username}->{usernm_to}: {msg}'
            
            user_to = None
            for ws in self.get_by_key(usernm_to):
                if ws != self:
                    user_to = ws._user
                    ws.send(message)

            if user_to == None:
                user_to = User.objects.filter(username=usernm_to)
                if len(user_to) != 0:
                    user_to = user_to[0]
                else:
                    user_to = None
            
            if user_to != None:
                for ws in self.get_key_like():
                    if ws != self:
                        ws.send(message)
                
                Message.objects.create(author=user_from, receiver=user_to, message=msg)

        if datas[0] == 'CHALLENGE':
            user_from = self._user
            usernm_to = datas[1]
            user_to = User.objects.filter(username=usernm_to)
            chl_format = ': '.join(datas[2:])
            if len(user_to) != 0:
                user_to = user_to[0]
            else:
                user_to = None
            
            if user_to != None:
                if ' - ' in chl_format:
                    try:
                        tournament = Tournament.objects.filter(tournament_name=chl_format.split(' - ')[0])[0]
                        game = Game.objects.filter(Q(player1=user_from, player2=user_to) | Q(player2=user_from,player1=user_to), tournament=tournament)[0]
                    
                        if game.score1 < game.score_needed and game.score2 < game.score_needed:
                            chess_game = game.games.filter(start_time=1)
                            if len(chess_game) != 1:
                                p1 = game.player1 if game.games.count() % 2 == 0 else game.player2
                                p2 = game.player2 if game.games.count() % 2 == 0 else game.player1
                                chess_game = [ChessGame.objects.create(start_board="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                                player1 = p1, player2 = p2, start_time = 1, list_move="", format=game.time_format)]
                                game.games.add(chess_game[0])
                            chess_game = chess_game[0]

                            if self._invit != None:
                                self._invit.close()
                            self._invit = Invitation.objects.create(author=user_from, receiver=user_to, game=chess_game)
                            
                            for ws in self.get_by_key(user_from.username):
                                ws.send(f'INVIT: {user_from.username}->{user_to.username}: {self._invit.id}')

                            for ws in self.get_by_key(user_to.username):
                                ws.send(f'INVIT: {user_from.username}->{user_to.username}: {self._invit.id}')
                    except Exception as e:
                        print(e)
                else:
                    player1 = self._user
                    player2 = user_to
                    if random.randint(0, 1) == 0:
                        player1 = user_to
                        player2 = self._user
                    game = ChessGame.objects.create(start_board="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                                player1 = player1, player2 = player2, start_time = 1, list_move="", format=chl_format)
                    self._invit = Invitation.objects.create(author=user_from, receiver=user_to, game=game)
                    for ws in self.get_by_key(user_from.username):
                        ws.send(f'INVIT: {user_from.username}->{user_to.username}: {self._invit.id}')

                    for ws in self.get_by_key(user_to.username):
                        ws.send(f'INVIT: {user_from.username}->{user_to.username}: {self._invit.id}')
 
        if datas[0] == 'ACCEPT':
            try:
                invit = Invitation.objects.filter(receiver=self._user, id=int(datas[1]))[0]
                if self._invit != None:
                    self._invit.close()
                
                other = None
                for ws in self.get_by_key(invit.author.username):
                    if ws._invit.id == invit.id:
                        other = ws
                        break
                
                if other != None:
                    invit.game.start_time = int(time.time() * 1000)
                    invit.game.save()

                    self.send(f'REDIRECT: /games/{invit.game.id}')
                    other.send(f'REDIRECT: /games/{invit.game.id}')
                    print('STARTED')
                    invit.close()

            except Exception as e:
                print(e)

        return super().receive(text_data=text_data, bytes_data=bytes_data)
    def disconnect(self, code):
        if self._invit != None:
            self._invit.close()
        return super().disconnect(code)

######################
# SOCIAL ROUTER      #
######################

class SocialRouter(BaseRouter):
    default_path = 'social/'
    path_array   = [
        ('', SocialHomeView(), 'social.index'),
    ]

################
# WS ROUTER    #
################

class WebSocketSocialRouter(BaseRouter):
    default_path = 'ws/social/'
    path_array   = [
        ('', WSSocialView.as_asgi(), 'ws.social.home_listener')
    ]

from social.models import Invitation, Message