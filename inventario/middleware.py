from django.shortcuts import reverse, redirect
from django.contrib.auth import logout

class GroupRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='videotecaPermission').exists():
                # Redireccionar si no coincide con rutas específicas
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
                    not request.path.startswith('/search_folio/') and
                    not request.path.startswith('/detail_folio/') and
                    not request.path.startswith('/register_in/') and
                    not request.path.startswith('/validate_out/') and
                    not request.path.startswith('/register_out/') and
                    not request.path.startswith('/end_in/') and
                    not request.path.startswith('/get_report/') and
                    not request.path.startswith('/cintas/inventarioRegistro/') and
                    not request.path.startswith('/cintas/consultaInventario/') and
                    not request.path.startswith('') and
                    not request.path.startswith(reverse('logout'))
                ):
                    return redirect('prestamos_list')
            elif request.user.groups.filter(name='calificacion').exists():
                # Redireccionar si no coincide con rutas específicas
                if (
                    request.path != reverse('consultaFormulario') and
                    # not request.path.startswith('/calificaciones/formulario/') and
                    not request.path.startswith('/calificaciones/formulario/') and
                    not request.path.startswith('/calificaciones/agregar/programa/') and
                    not request.path.startswith('/calificaciones/editar/') and
                    not request.path.startswith('/calificaciones/editar/programa/') and
                    not request.path.startswith('/calificaciones/eliminar/') and
                    not request.path.startswith('/calificaciones/eliminarRegistro/') and
                    not request.path.startswith('/calificaciones/cambiarEstatusCalificacion/') and
                    not request.path == reverse('formulario') and
                    not request.path.startswith(reverse('logout'))
                ):
                    return redirect('consultaFormulario')

        response = self.get_response(request)
        return response
