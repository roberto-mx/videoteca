from django.shortcuts import reverse, redirect
from django.contrib.auth import logout

class GroupRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificamos si el usuario está autenticado
        if request.user.is_authenticated:
            # Verificamos si el usuario pertenece al grupo 'videotecaPermission'
            if request.user.groups.filter(name='videotecaPermission').exists():
                # Si el usuario intenta acceder a una ruta diferente a 'prestamos_list',
            
                if request.path != reverse('prestamos_list'):
                    return redirect('prestamos_list')
            # Verificamos si el usuario pertenece al grupo 'calificacion'
            elif request.user.groups.filter(name='calificacion').exists():
                # si el usuario accede a otra ruta que no sea de calificaciones se le redirige a consulta formulario
                if (
                    request.path != reverse('consultaFormulario') and
                    not request.path.startswith('/calificaciones/agregar/') and
                    not request.path.startswith('/calificaciones/editar/') and
                    not request.path.startswith('/calificaciones/eliminar/') and
                    not request.path.startswith('/calificaciones/eliminarRegistro/') and
                    not request.path.startswith('/calificaciones/cambiarEstatusCalificacion/') and
                    request.path != reverse('formulario')
                ):
                    return redirect('consultaFormulario')

        # Si el usuario no cumple ninguna de las condiciones anteriores,
        # pasamos la solicitud al siguiente middleware
        response = self.get_response(request)
        return response

