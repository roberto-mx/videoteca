from django.shortcuts import reverse, redirect
from django.contrib.auth import logout

# class GroupRedirectMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if request.user.is_authenticated:
#             if request.user.groups.filter(name='videotecaPermission').exists() and request.path != reverse('prestamos_list'):
#                 return redirect('prestamos_list')
#             elif request.user.groups.filter(name='calificacion').exists() and request.path != reverse('consultaFormulario'):
#                 return redirect('consultaFormulario')

#         response = self.get_response(request)
#         return response


class GroupRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            
            if request.user.groups.filter(name='videotecaPermission').exists():
                if request.path != reverse('prestamos_list'):
                    logout(request)
                    return redirect('prestamos_list')
            elif request.user.groups.filter(name='calificacion').exists():
                if request.path != reverse('consultaFormulario'):
                    logout(request)
                    return redirect('consultaFormulario')

        response = self.get_response(request)
        return response
