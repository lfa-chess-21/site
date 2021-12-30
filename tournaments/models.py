

from django.db import models
from django.contrib.auth.models import User
from games.models import ChessGame

class Game(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pl1")
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pl2")
    
    score_needed = models.IntegerField()
    score1 = models.IntegerField()
    score2 = models.IntegerField()

    time_format = models.CharField(max_length=10)
    games = models.ManyToManyField(ChessGame)

    tournament     = models.ForeignKey('Tournament', default=1, on_delete=models.CASCADE, related_name='game_in_tournament')

    def is_over(self):
        return self.score1 > self.score_needed or self.score2 > self.score_needed
    def get_won_player(self):
        if self.score1 > self.score_needed:
            return self.player1
        if self.score2 > self.score_needed:
            return self.player2
        return None
    

class Round(models.Model):
    left_has_next  = models.BooleanField(default=False)
    left_round     = models.ForeignKey("Round", default=0, on_delete=models.CASCADE, related_name="l_round")

    right_has_next = models.BooleanField(default=False)
    right_round    = models.ForeignKey("Round", default=0, on_delete=models.CASCADE, related_name="r_round")

    current_game   = models.ForeignKey(Game, default=0, on_delete=models.CASCADE, related_name="game") 
    tournament     = models.ForeignKey('Tournament', default=1, on_delete=models.CASCADE, related_name='in_tournament')

class Tournament(models.Model):
    final_round       = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='f_round')
    tournament_name   = models.CharField(max_length=200)
    tournament_format = models.CharField(max_length=200)

    players = models.ManyToManyField(User)

    tournament_format_description = models.TextField()

    start          = models.DateField(default='1970-01-01')
    end            = models.DateField(default='1970-01-01')
    is_open        = models.BooleanField(default=False)
    subscribe_date = models.DateField(default='1970-01-01')
