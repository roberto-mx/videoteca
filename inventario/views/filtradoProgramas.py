from django.shortcuts import render
from ..models import ProgramaSeries, MaestroCintas, RegistroCalificacion
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Value, CharField, F

@csrf_exempt

@csrf_exempt
def filtrarBusqueda(request):
    if request.method == 'GET':
        serie = request.GET.get('serie', '')
        subtituloSerie = request.GET.get('subtituloSerie', '')
        programa = request.GET.get('programa', '')
        subtituloPrograma = request.GET.get('subtituloPrograma', '')
        codigo_barras = request.GET.get('codigo_barras', '')
        sinopsis = request.GET.get('sinopsis', '')

        # Inicializar cat_status con un valor predeterminado
        cat_status = None

        # Filtrar ProgramaSeries
        resultados_programaseries = ProgramaSeries.objects.filter(
            serie__icontains=serie,
            subtituloSerie__icontains=subtituloSerie,
            programa__icontains=programa,
            subtituloPrograma__icontains=subtituloPrograma,
            codigo_barras__video_cbarras__icontains=codigo_barras,
            sinopsis__icontains=sinopsis
        )

        # Combinar resultados de ambas tablas
        data = []
        if resultados_programaseries.exists():
            for resultado in resultados_programaseries:
                try:
                    maestro_cintas = MaestroCintas.objects.get(video_cbarras=resultado.codigo_barras_id)
                    cat_status = maestro_cintas.video_tipo
                    print(cat_status)

                    data.append({
                        'codigo_barras': resultado.codigo_barras.video_cbarras,
                        'serie': resultado.serie,
                        'programa': resultado.programa,
                        'subtituloPrograma': resultado.subtituloPrograma,
                        'tipo': cat_status.status,
                        'estatus': maestro_cintas.video_estatus
                    })
                except MaestroCintas.DoesNotExist:
                    print(f"MaestroCintas not found for video_cbarras: {resultado.codigo_barras_id}")
        else:
            # Filtrar RegistroCalificacion si no hay resultados en ProgramaSeries
            resultados_registro_calificacion = RegistroCalificacion.objects.filter(
                serie__icontains=serie,
                programa__icontains=programa,
                subtitulo_programa__icontains=subtituloPrograma,
                codigo_barras__video_cbarras__icontains=codigo_barras,
                sinopsis__icontains=sinopsis
            )

            for resultado in resultados_registro_calificacion:
                try:
                    maestro_cintas = MaestroCintas.objects.get(video_cbarras=resultado.codigo_barras_id)
                    cat_status = maestro_cintas.video_tipo
                    

                    data.append({
                        'codigo_barras': resultado.codigo_barras.video_cbarras,
                        'serie': resultado.serie,
                        'programa': resultado.programa,
                        'subtituloPrograma': resultado.subtitulo_programa,
                        'tipo': cat_status.status,
                        'estatus': maestro_cintas.video_estatus
                    })
                except MaestroCintas.DoesNotExist:
                    print(f"MaestroCintas not found for video_cbarras: {resultado.codigo_barras_id}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'data': data}, safe=False)
        else:
            
            return render(request, 'calificaForm/filtrarBusqueda.html', {'data': data})
