from django.db import models
from django.contrib.auth.models import User

import random
import string

from games.models import ChessGame

def generate_invitation_key():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

class Message(models.Model):
    author   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_author")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_receiver")

    message = models.CharField(max_length=400)

class Invitation(models.Model):
    author   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invt_author")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invt_receiver")
    
    game = models.ForeignKey(ChessGame, on_delete=models.CASCADE)

    def close(self):
        for ws in WSSocialView.get_by_key(WSSocialView(), self.author.username):
            ws.send(f'CLOSE_INVIT: {self.author.username}->{self.receiver.username}: {self.game.id}')

        for ws in WSSocialView.get_by_key(WSSocialView(), self.receiver.username):
            ws.send(f'CLOSE_INVIT: {self.author.username}->{self.receiver.username}: {self.game.id}')
        self.delete()

from social.views import WSSocialView