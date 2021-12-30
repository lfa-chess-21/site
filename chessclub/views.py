
################
# IMPORTS      #
################

from channels.routing import URLRouter
from django.http          import Http404
from django.http.response import JsonResponse
from django.urls          import reverse, path, include
from django.shortcuts     import redirect, render
from django.contrib.staticfiles.views import serve 

################
# STATIC FILES #
################

def custom_serve(request, path, insecure=False, **kwargs):
    """
    Customize the response of serving static files.

    Note:
        This should only ever be used in development, and never in production.
    """
    response = serve(request, path, insecure=True)

    response['Cross-Origin-Opener-Policy']   = 'same-origin'
    response['Cross-Origin-Embedder-Policy'] = 'require-corp'
    # if path.endswith('sw.js'):
    #    response['Service-Worker-Allowed'] = '/'
    return response

################
# DEFAULT VIEW #
################

class BaseView:

    ################
    # PERMISSIONS  #
    ################

    needs_anonymous  = False
    needs_connection = False
    needs_staff      = False

    ## When the permission were not correct, choose how to redirect the user
    error            = Http404()
    redirector       = 'home'

    def has_permissions(self):
        return  (not self.needs_anonymous  or not self.request.user.is_authenticated) \
            and (not self.needs_connection or     self.request.user.is_authenticated) \
            and (not self.needs_staff      or     self.request.user.is_staff)
    def raise_permission_error(self):
        if self.error != None:
            raise self.error
        return redirect(reverse(self.redirector, kwargs=self.get_redirector_kwargs()))

    def get_redirector_kwargs(self):
        return {}
    
    ###################
    # MAIN FUNCTIONS  #
    ###################

    def __init__(self):
        pass
    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.args    = args
        self.kwargs  = kwargs

        if not self.has_permissions():
            return self.raise_permission_error()
        
        if self.request.method == 'GET':
            return self.handle_get_request()
        if self.request.method == 'POST':
            return self.handle_post_request()
        return self.raise_permission_error()
    
    #####################
    # REQUEST HANDLERS  #
    #####################

    has_template  = True
    template_name = 'home/index.html'

    has_post_request   = False
    post_args          = []
    post_redirect_name = None

    def get_context_data(self):
        return {}

    def handle_get_request(self):
        if not self.has_template:
            return self.raise_permission_error()
        return render(self.request, self.template_name, self.get_context_data())
    
    def get_post_json(self):
        return {}
    def finish_post_request(self):
        ## If has something in URL like next=/ redirect to this
        if self.post_redirect_name != None:
            if self.post_redirect_name in self.request.GET:
                return redirect(self.request.GET[self.post_redirect_name])
        
        return JsonResponse(self.get_post_json())
    def handle_post(self): ## Function that needs to be implemented
        return self.finish_post_request()
    def handle_post_request(self):
        if not self.has_post_request:
            return self.raise_permission_error()

        for post_arg_expected in self.post_args:
            if not post_arg_expected in self.request.POST:
                return self.raise_permission_error()
        
        return self.handle_post()

                

################
# ROUTER       #
################

class BaseRouter:
    path_array   = []
    default_path = '/'
    
    def __init__(self):
        pass
    def get_built_path(self):
        built_path = []

        for tup in self.path_array:
            str_path, handler = None, None
            name = ''
            if len(tup) == 2:
                str_path, handler = tup
            else:
                str_path, handler, name = tup
            built_path.append(path(str_path, handler, name=name))
        
        return built_path
    def get_include(self):
        return path(self.default_path, include(self.get_built_path()))
    def get_ws_include(self):
        return path(self.default_path, URLRouter(self.get_built_path()))