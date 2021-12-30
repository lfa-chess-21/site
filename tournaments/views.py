
######################
# IMPORTS            #
######################

from chessclub.views import BaseView, BaseRouter
from tournaments.models import Tournament
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
import datetime

################
# VIEWS        #
################

class TournamentHomeView(BaseView):
    template_name = 'tournaments/home.html'

    def get_context_data(self):
        default = super().get_context_data()

        default['tournaments'] = Tournament.objects.all()[:10]

        return default

class TournamentView(BaseView):
    template_name = 'tournaments/tournament.html'

    def get_context_data(self):
        default = super().get_context_data()

        default['tournament'] = get_object_or_404(Tournament, id=self.kwargs['uuid'])
        if self.request.user.is_authenticated:
            default['subscribed'] = default['tournament'].players.filter(id=self.request.user.id).count() != 0

        default['rounds'] = [[default['tournament'].final_round]]
        while default['rounds'][-1].count(None) != len(default['rounds'][-1]):
            self.build_default_row(default)
        default['now'] = datetime.date.today()

        return default
    def build_default_row(self, default):
        crow = default['rounds'][-1]
        nrow = []
        for obj in crow:
            if obj == None:
                nrow.append(None)
                nrow.append(None)
            else:
                nrow.append(obj.left_round if obj.left_has_next else None)
                nrow.append(obj.right_round if obj.right_has_next else None)
        default['rounds'].append(nrow)

class TournamentToggleView(BaseView):
    needs_connection = True
    def handle_get_request(self):
        tournament = get_object_or_404(Tournament, id=self.kwargs['uuid'])
        if tournament.players.filter(id=self.request.user.id).count() != 0:
            tournament.players.remove(self.request.user)
        else:
            tournament.players.add(self.request.user)

        return redirect(reverse('tournament.tournament', kwargs=self.kwargs))

######################
# TOURNAMENTS ROUTER #
######################

class TournamentsRouter(BaseRouter):
    default_path = 'tournaments/'
    path_array   = [
        ('', TournamentHomeView(), 'tournament.index'),
        ('<int:uuid>/', TournamentView(), 'tournament.tournament'),
        ('<int:uuid>/toggle', TournamentToggleView(), 'tournament.toggle_subscription')
    ]