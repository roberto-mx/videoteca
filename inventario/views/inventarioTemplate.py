from django.shortcuts import render, redirect
from ..forms import  MaestrosCintasForm
from ..models import MaestroCintas, FormatosCintas, CatStatus 
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import JsonResponse
import json
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
# 

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import re


@login_required
def inventarioRegistro(request):
    if request.method == 'POST':
        form = MaestrosCintasForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({ 'message': "¡Se ha registrado la cinta con éxito!"})
    else:
        form = MaestrosCintasForm()

    return render(request, 'inventario/inventarioRegistro.html', {'formulario': form})



@login_required
@csrf_exempt
def consultaInventario(request):
    cbarras = request.GET.get('q', '')
    formato = request.GET.get('formato', '')
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    anio = request.GET.get('anio', '')

    no_search_result = cbarras != '' or formato != '' or tipo != '' or status != '' or anio != ''

    estatus = {
        '1': 'En Videoteca',
        '2': 'En Calificacion',
        '3': 'Cinta Extraviada',
        '4': 'Baja por Daño'
    }

    rs = MaestroCintas.objects.all().order_by('video_cbarras')

    if cbarras != '':
        rs = rs.filter(video_cbarras__contains=cbarras)
    if formato != '':
        rs = rs.filter(form_clave=formato)
    if tipo != '':
        rs = rs.filter(video_tipo=tipo)
    if status != '':
        rs = rs.filter(video_estatus=estatus.get(status, ''))  # Obtener el valor correspondiente o cadena vacía
    if anio != '':
        rs = rs.filter(video_fechamov__year=int(anio))

    query_string = request.META.get("QUERY_STRING", "")
    validated_query_string = "&".join([x for x in re.findall(r"(\w*=\w{1,})", query_string) if not "page=" in x])

    page = request.GET.get('page')
    paginate_by = 1000
    paginator = Paginator(rs, paginate_by)

    try:
        cintas = paginator.page(page)
    except PageNotAnInteger:
        cintas = paginator.page(1)
    except EmptyPage:
        cintas = paginator.page(paginator.num_pages)

    context = {
        'mcintas_list': cintas,
        'tipo_list': CatStatus.objects.all(),
        'formatos_list': FormatosCintas.objects.all(),
        'no_search_result': no_search_result,
        'query_string': "&" + validated_query_string if (validated_query_string and no_search_result) else "",
        'cbarras_filter': cbarras,
        'formato_filter': int(formato) if formato != '' else 0,
        'tipo_filter': tipo,
        'status_filter': status,
        'anio_filter': anio,
    }

    return render(request, 'inventario/consultaInventario.html', context)

