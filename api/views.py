
################
# IMPORTS      #
################

from chessclub.views     import BaseView, BaseRouter
from django.contrib.auth import authenticate, login, logout, models
from django.shortcuts    import redirect
from django.contrib      import messages

################
# VIEWS        #
################

class ApiHomeView(BaseView):
    template_name = 'api/index.html'

class ApiLoginView(BaseView):
    ## Disable GET request
    has_template    = False
    needs_anonymous = True
    
    ## Enable POST request
    has_post_request   = True
    post_arguments     = [
        'username',
        'password'
    ]
    post_redirect_name = 'next'

    def get_post_json(self):
        return { 'success':self.request.user.is_authenticated }
    def finish_post_request(self):
        if self.post_redirect_name in self.request.GET:
            if self.request.user.is_anonymous:
                return redirect('/account/login/?next=' + self.request.GET[self.post_redirect_name])
        return super().finish_post_request()

    def handle_post(self):
        username = self.request.POST['username']
        password = self.request.POST['password']

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if self.post_redirect_name in self.request.GET: 
                messages.success(self.request, 'Connection réussie')
            login(self.request, user)
        else:
            if self.post_redirect_name in self.request.GET:
                messages.error(self.request, 'Une erreur est survenue lors de la connection')
            pass

        return self.finish_post_request()

class ApiLogoutView(BaseView):
    ## Enable POST request
    has_post_request   = True
    post_arguments     = []
    post_redirect_name = 'next'

    def get_post_json(self):
        return { 'success':self.request.user.is_anonymous }
    def handle_post(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return self.finish_post_request()
    def handle_get_request(self):
        return self.handle_post()


class ApiCreateAccountView(BaseView):
    ## Disable GET request
    has_template    = False
    needs_anonymous = True
    
    ## Enable POST request
    has_post_request   = True
    post_arguments     = [
        'username',
        'password',
        'password_repeat'
    ]
    post_redirect_name = 'next'

    def get_post_json(self):
        return { 'success':self.request.user.is_authenticated }
    def finish_post_request(self, err=''):
        if self.post_redirect_name in self.request.GET:
            if self.request.user.is_anonymous:
                if err != '':
                    return redirect('/account/create/?next=' + self.request.GET[self.post_redirect_name] + '&err=' + err)
                return redirect('/account/create/?next=' + self.request.GET[self.post_redirect_name])
        return super().finish_post_request()

    def handle_post(self):
        username = self.request.POST['username']
        password = self.request.POST['password']
        password2 = self.request.POST['password_repeat']
        if password != password2 \
        or len(password) < 8 or len(password) > 20:
            return self.finish_post_request()

        try:
            print('Creating')
            models.User.objects.create_user(username, '', password)
        except Exception:
            print('err')
            return self.finish_post_request('Ce compte existe déjà')

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            if self.post_redirect_name in self.request.GET: 
                messages.success(self.request, 'Connection réussie')
            login(self.request, user)
        else:
            if self.post_redirect_name in self.request.GET:
                messages.error(self.request, 'Une erreur est survenue lors de la connection')
            pass

        return self.finish_post_request()

################
# API ROUTER   #
################

class ApiRouter(BaseRouter):
    default_path = 'api/'
    path_array   = [
        ('index/',  ApiHomeView(),   'api.index'),
        ('login/',  ApiLoginView(),  'api.account.login'),
        ('logout/', ApiLogoutView(), 'api.account.logout'),
        ('create/account/', ApiCreateAccountView(), 'api.account.create')
    ]
