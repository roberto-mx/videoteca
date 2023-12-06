from django.shortcuts import render
from ..models import ProgramaSeries, MaestroCintas, CatStatus
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.serializers import serialize

@csrf_exempt
def filtrarBusqueda(request):
    if request.method == 'GET':
        serie = request.GET.get('serie', '')
        subtituloSerie = request.GET.get('subtituloSerie', '')
        programa = request.GET.get('programa', '')
        subtituloPrograma = request.GET.get('subtituloPrograma', '')
        codigo_barras = request.GET.get('codigo_barras', '')
        sinopsis = request.GET.get('sinopsis', '')

        resultados_programaseries = ProgramaSeries.objects.filter(
            serie__icontains=serie,
            subtituloSerie__icontains=subtituloSerie,
            programa__icontains=programa,
            subtituloPrograma__icontains=subtituloPrograma,
            codigo_barras__video_cbarras__icontains=codigo_barras,
            sinopsis__icontains=sinopsis
        )

        data = []
        for resultado in resultados_programaseries:
            maestro_cintas = MaestroCintas.objects.get(video_cbarras=resultado.codigo_barras_id)
            cat_status = maestro_cintas.video_tipo
            data.append({
                'codigo_barras': resultado.codigo_barras.video_cbarras,
                'serie': resultado.serie,
                'programa': resultado.programa,
                'subtituloPrograma': resultado.subtituloPrograma,
                'tipo': cat_status.status,
                'estatus': maestro_cintas.video_estatus
            })

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            return JsonResponse({'data': data}, safe=False)
        else:
            return render(request, 'calificaForm/filtrarBusqueda.html', {'data': data})

# def filtrarBusqueda(request):
#     if request.method == 'GET':
#         serie = request.GET.get('serie', '')
#         subtituloSerie = request.GET.get('subtituloSerie', '')
#         programa = request.GET.get('programa', '')
#         subtituloPrograma = request.GET.get('subtituloPrograma', '')
#         codigo_barras = request.GET.get('codigo_barras', '')
#         sinopsis = request.GET.get('sinopsis', '')

#         # Filtrar los resultados según los parámetros de búsqueda
#         resultados_programaseries = ProgramaSeries.objects.filter(
#             serie__icontains=serie,
#             subtituloSerie__icontains=subtituloSerie,
#             programa__icontains=programa,
#             subtituloPrograma__icontains=subtituloPrograma,
#             codigo_barras__video_cbarras__icontains=codigo_barras,
#             sinopsis__icontains=sinopsis
#         )
#         print(resultados_programaseries)  # Verifica si hay resultados aquí

#         # Obtener los datos necesarios y devolverlos como JSON
#         data = []
#         for resultado in resultados_programaseries:
#             maestro_cintas = MaestroCintas.objects.get(video_cbarras=resultado.codigo_barras_id)
#             cat_status = maestro_cintas.video_tipo  # Obtener la instancia de CatStatus
#             data.append({
#                 'codigo_barras': resultado.codigo_barras.video_cbarras,
#                 'serie': resultado.serie,
#                 'programa': resultado.programa,
#                 'subtituloPrograma': resultado.subtituloPrograma,
#                 'tipo': cat_status.status,
#                 'estatus': maestro_cintas.video_estatus
#             })

#         # return JsonResponse(data, safe=False)
#         print(data)

#     return render(request, 'calificaForm/filtrarBusqueda.html', {'data': data})

