
#################
# IMPORTS       #
#################

from chessclub.views     import BaseView, BaseRouter
from django.urls         import reverse
from django.shortcuts    import redirect

#################
# VIEWS         #
#################

class AccountLoginView(BaseView):
    ## Template (GET Request)
    template_name = 'account/login.html'

    ## Permissions
    needs_anonymous = True

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx['next'] = '/'
        if 'next' in self.request.GET:
            ctx['next'] = ctx['next']
        
        return ctx

    def raise_permission_error(self):
        if self.request.user.is_authenticated:
            return redirect(reverse('account.settings'))
        return super().raise_permission_error()

class AccountSettingsView(BaseView):
    ## Template (GET Request)
    template_name = 'account/settings.html'

    ## Permissions
    needs_connection = True

    def raise_permission_error(self):
        if self.request.user.is_anonymous:
            return redirect(reverse('account.login'))
        return super().raise_permission_error()

class AccountCreateView(BaseView):
    ## Template (GET Request)
    template_name = 'account/create.html'

    ## Permissions
    needs_anonymous = True

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx['next'] = '/'
        if 'next' in self.request.GET:
            ctx['next'] = self.request.GET['next']
        if 'err' in self.request.GET:
            ctx['err'] = self.request.GET['err']
        
        return ctx

    def raise_permission_error(self):
        if self.request.user.is_authenticated:
            return redirect(reverse('account.settings'))
        return super().raise_permission_error()

##################
# ACCOUNT ROUTER #
##################

class AccountRouter(BaseRouter):
    default_path = 'account/'
    path_array   = [
        ('login/',    AccountLoginView(),    'account.login'),
        ('settings/', AccountSettingsView(), 'account.settings'),
        ('create/',   AccountCreateView(),   'account.create')
    ]
