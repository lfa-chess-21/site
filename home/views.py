
################
# IMPORTS      #
################

from chessclub.views  import BaseView, BaseRouter
from home.models import ForumPost

################
# VIEWS        #
################

class HomeView(BaseView):
    template_name = 'home/index.html'

    def get_context_data(self):
        default = super().get_context_data()

        default['posts'] = ForumPost.objects.order_by('-date')

        return default

################
# HOME ROUTER  #
################

class HomeRouter(BaseRouter):
    default_path = ''
    path_array   = [
        ('index', HomeView(), 'home.index'),
        ('',      HomeView(), 'home')
    ]
