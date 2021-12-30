
#####################
# IMPORTS           #
#####################

from django.contrib.auth.models import User
from django.db.models.deletion  import CASCADE
from django.db                  import models
from functools                  import cached_property

import calendar

#####################
# POST ON HOME PAGE #
#####################

class ForumPost(models.Model):
    author       = models.ForeignKey(User, on_delete=CASCADE)
    date         = models.DateTimeField()
    title        = models.CharField(max_length=200)
    text         = models.CharField(max_length=200)
    visible      = models.BooleanField(default=True)
    date_visible = models.BooleanField(default=True)

    @cached_property
    def get_month(self):
        ## French month names
        return [
            'janvier', 'février', 'mars', 
            'avril', 'mai', 'juin', 
            'juillet', 'août', 'septembre',
            'octobre', 'novembre', 'décembre'
        ][self.date.month - 1]
