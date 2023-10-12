from django.shortcuts import reverse, redirect
from django.contrib.auth import logout

class GroupRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       
        if request.user.is_authenticated:
            
            if request.user.groups.filter(name='videotecaPermission').exists():
                # Si el usuario intenta acceder a una ruta diferente a 'prestamos_list',
                if (
                    request.path != reverse('prestamos_list') and
                    not request.path.startswith('/prestamos/') and
                    not request.path.startswith('/prestamos/detalles_list/') and
                    not request.path.startswith('/prestamos/detalles/') and
                    not request.path.startswith('/prestamos/detalles/filter/') and
                    not request.path.startswith('/prestamos/generate_pdf/') and
                    not request.path.startswith('/prestamos/generate_pdf_modal/') and
                    not request.path.startswith('/prestamos/person_people/') and

                    not request.path.startswith('/prestamos/generate_pdf_register/') and
                    not request.path.startswith('/search_folio/<int:pk>/') and
                    not request.path.startswith('/detail_folio/<int:pk>/') and
                    not request.path.startswith('/register_in/') and
                    not request.path.startswith('/validate_out/') and
                    not request.path.startswith('/register_out/') and
                    not request.path.startswith('/end_in/') and
                    not request.path.startswith('/get_report/') and

                    not request.path.startswith(reverse('logout'))
                ):
                    return redirect('prestamos_list')

            # Verificamos si el usuario pertenece al grupo 'calificacion'
            elif request.user.groups.filter(name='calificacion').exists():
                # si el usuario accede a otra ruta que no sea de calificaciones se le redirige a consulta formulario
                if (
                    request.path != reverse('/consultaFormulario/') and
                    not request.path.startswith('/calificaciones/agregar/programa/<str:codigo_barras>') and
                    not request.path.startswith('/calificaciones/editar/<int:id>/<str:codigo_barras>/') and
                    not request.path.startswith('/calificaciones/editar/programa/<int:programa_id>/') and
                    not request.path.startswith('/calificaciones/eliminar/<int:id>/') and
                    not request.path.startswith('/calificaciones/eliminarRegistro/<int:id>/') and
                    not request.path.startswith('/calificaciones/cambiarEstatusCalificacion/<int:id>/') and
                    request.path != reverse('formulario') and
                    not request.path.startswith(reverse('logout'))
                ):
                    return redirect('consultaFormulario')

        response = self.get_response(request)
        return response

