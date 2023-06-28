from django.views.generic import ListView
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from ..forms import PrestamoInlineFormset
from .reports import json_to_pdf
from django.shortcuts import render
from functools import reduce
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import textwrap, operator, base64, json
from django.template.loader import get_template
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404
import tempfile
import os

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from django.utils import timezone
import pandas as pd
from django.db import connections


    # ---------------------------
    # Prestamos
    # ---------------------------
def Filtrar_prestamos(request):
    q = request.GET.get('q')

    prestamos_data = []

    if q:
        prestamos = DetallePrestamos.objects.filter(
            Q(pres_folio=q) | Q(vide_codigo=q)
        )

        for prestamo in prestamos:
            prestamo_data = {
                "pres_folio": prestamo.pres_folio.pres_folio,
                "usua_clave": prestamo.pres_folio.usua_clave,
                "pres_fechahora": prestamo.pres_folio.pres_fechahora,
                "pres_fecha_devolucion": prestamo.pres_folio.pres_fecha_devolucion,
                "pres_estatus": prestamo.pres_folio.pres_estatus
            }
            prestamos_data.append(prestamo_data)

    return JsonResponse(prestamos_data, safe=False)

@method_decorator(login_required, name='dispatch')

class PrestamosListView(ListView):
    def get(self, request):
        current_year = datetime.now().year
        queryset = Prestamos.objects.filter(pres_fecha_prestamo__year__gte=current_year).order_by('-pres_fechahora')
        context = {
            'prestamos': queryset,
        }
        return render(request, 'prestamos/prestamos_list.html', context)
    
#vista detalle    
@csrf_exempt
def DetallesListView(request):
    q = request.GET.get('q')
    fecha_actual = datetime.now()  # Fecha y hora actual del servidor
    hace_siete_dias = fecha_actual - timedelta(days=7)  # Fecha y hora hace 7 días

    queryset = Prestamos.objects.filter(usua_pres_fecha_prestamo__year='2022', usua_clave=q).order_by('-pres_fechahora')
    template_detalle = {
        'prestamos': queryset,
        'fecha_actual': fecha_actual,
        'hace_siete_dias': hace_siete_dias,
    }

    # print(template_detalle)
    return render(request, 'prestamos/detalles_list.html', template_detalle)

@csrf_exempt
def obtenerPeoplePerson(request):
    fecha_actual = datetime.now().date()  # Fecha y hora actual del servidor
    fecha_actual_formato = fecha_actual.strftime('%d-%m-%Y')
    hace_siete_dias = fecha_actual - timedelta(days=7)  # Fecha y hora hace 7 días

    # print(fecha_actual)

    q = request.GET.get('q')
    prestamo = Prestamos.objects.filter(pres_folio=q).values('usua_clave','pres_fecha_prestamo').first()

    matri = None
    if prestamo is not None:
        matri = prestamo['usua_clave']
        fechaPrestamo = prestamo['pres_fecha_prestamo'].strftime('%d-%m-%Y')
        # print(fechaPrestamo)

    if matri is not None:
        cursor = connections['users'].cursor()
        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [matri])

        row = cursor.fetchone()

        MatriculaObPrestamo = {}

        if row is not None:
            nombres                 = row[0]
            apellido1               = row[1]
            apellido2               = row[2]
            puesto                  = row[3]
            email_institucional     = row[4]
            extension_telefonica    = row[5]

            nombre_completo = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
            MatriculaObPrestamo = {
                'Obtiene'           : nombre_completo,
                'Puesto'            : puesto,
                'Email'             : email_institucional,
                'Extension'         : extension_telefonica, 
                'Matricula'         : matri,
                'PrestamoFecha'     : fechaPrestamo,
                'fechaActual'       : fecha_actual_formato,
                'tiempoDevolucion'  : hace_siete_dias,
            }
            
    return JsonResponse(MatriculaObPrestamo, safe=False)

@csrf_exempt
def PrestamoDetalle(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion','usuario_devuelve','usuario_recibe')
    context = { 'detalles': queryset }
    return render(request, 'prestamos/prestamos_detalle_list.html', context)

@csrf_exempt
def GetFolioPrestamo(request):
    q=request.GET.get("q")
    queryset =DetallePrestamos.objects.filter(Q(pres_folio__pres_fecha_prestamo__year = '2022')).order_by('-pres_folio__pres_fechahora')
    if q and q !=" ":
        #q =q.split(" ")
        if q.isnumeric():
            query = (Q(pres_folio__pres_folio=q) | Q(vide_clave__vide_codigo=q )) 
        else:
            query = (Q(pres_folio__usua_clave__icontains=q) ) 
        queryset = queryset.filter(query)    

    t = get_template('prestamos/folio_search.html')
    content = t.render(
    {
        'prestamos': queryset, 
        #'compensacion' : list,
          
    })
    return HttpResponse(content)

@csrf_exempt
def GetFolioDetail(request):
    id=request.POST.get("id").strip()
    detailPrestamo =DetallePrestamos.objects.get(pres_folio = id)

    t = get_template('prestamos/detalle_prestamos.html')
    content = t.render(
    {
        #'cintas': videoDetail, 
        'detalles' : detailPrestamo,
          
    })
    return HttpResponse(content)

@csrf_exempt
def RegisterInVideoteca(request):
    usuario = request.POST['matricula']
    admin = request.user

    if request.method == 'POST':
        codigoBarras = request.POST['codigoBarras']
        now = datetime.now()

        # Llamar a la función ValidateOutVideoteca para comprobar si hay cintas faltantes
        validate_result = ValidateOutVideoteca(request)
        if validate_result.get('error', False):
            return JsonResponse(validate_result, safe=True)

        try:
            maestroCinta = MaestroCintas.objects.get(video_cbarras=codigoBarras)

            detallesPrestamo = DetallePrestamos.objects.filter(
                Q(vide_clave=maestroCinta.video_id) | Q(vide_codigo=codigoBarras)
            )

            if detallesPrestamo.exists():
                detallePrestamo = detallesPrestamo.latest('pres_folio')
            else:
                print("Hay que revisar los registros de este código de barras")
                registro_data = {
                    "error": True,
                    "errorMessage": "Hay que revisar los registros de este código de barras"
                }
                return JsonResponse(registro_data, safe=True)

            prestamo = Prestamos.objects.get(pres_folio=detallePrestamo.pres_folio_id)

            detallePrestamo.depr_estatus = 'I'
            detallePrestamo.pres_fecha_devolucion = now
            detallePrestamo.usuario_devuelve = usuario
            detallePrestamo.usuario_recibe = admin.username
            detallePrestamo.save()

            maestroCinta.video_estatus = 'En Videoteca'
            maestroCinta.save()

            prestamosActivos = DetallePrestamos.objects.filter(Q(pres_folio_id=prestamo.pk) & Q(depr_estatus='X'))
            if prestamosActivos.count() == 0:
                prestamo.pres_estatus = 'I'
                prestamo.pres_fecha_devolucion = now
                prestamo.save()

            registro_data = {
                "error": False,
                "errorMessage": "Registro Exitoso!"
            }
        except MaestroCintas.DoesNotExist:
            print("El código de barras no existe en Maestro Cintas")
            registro_data = {
                "error": True,
                "errorMessage": "El código de barras no existe en Maestro Cintas"
            }
        except Exception as e:
            print("Error:", str(e))
            registro_data = {
                "error": True,
                "errorMessage": "Ocurrió un error inesperado: " + str(e)
            }
        
    return JsonResponse(registro_data, safe=True)

@csrf_exempt  
def ValidateOutVideoteca(request):
    if request.method == 'POST':
        codigoBarras = request.POST.get('codigoBarras', '')
        usuario = request.POST.get('usuario', '')

        if not usuario or not codigoBarras:
            registro_data = {
                "error": True,
                "errorMessage": "Debes ingresar un usuario y un código de barras"
            }
        else:
            try:
                maestroCinta = MaestroCintas.objects.get(pk=codigoBarras)
                if maestroCinta.video_estatus == 'En Videoteca':
                    fecha_actual = datetime.now().date()
                    dias_habiles_encontrados = 0
                    desplazamiento = timedelta(days=1)

                    # Itero la fecha de los días hábiles tomando en cuenta los 7 días de la semana.
                    while dias_habiles_encontrados < 7:
                        fecha_actual -= desplazamiento
                        # Hago el desplazamiento de los días para no tomar en cuenta los fines de semana. 
                        if fecha_actual.weekday() < 5:
                            dias_habiles_encontrados += 1

                    # Convierto la fecha en formato legible.
                    fecha_vencimiento = fecha_actual.strftime('%Y-%m-%d')

                    # Hago la consulta para validar los folios vencidos, haciendo
                    # la comparación de pres_fecha_prestamo__lt a la fecha límite del préstamo.
                    folios_vencidos = Prestamos.objects.filter(
                        usua_clave=usuario,
                        pres_fecha_prestamo__lt=fecha_vencimiento,
                        # pres_fecha_devolucion__isnull=True
                    ).values('pres_folio').distinct()  # Obtengo el valor del Folio a través del modelo

                    for folio in folios_vencidos:
                        cintas_pendientes = DetallePrestamos.objects.filter(
                            pres_folio_id=folio['pres_folio'],
                            depr_estatus='X'
                        ).values_list('vide_codigo_id', flat=True)

                        cintas_faltantes = list(set(cintas_pendientes) - set([codigoBarras]))
                        print(cintas_faltantes)

                        if cintas_faltantes:
                            registro_data = {
                                "error": True,
                                "errorMessage": "El usuario debe devolver las cintas faltantes antes de solicitar nuevos préstamos",
                                "cintasFaltantes": cintas_faltantes
                            }
                            break
                    else:
                        # Verificar cintas pendientes por devolver
                        cintas_pendientes = DetallePrestamos.objects.filter(
                            depr_estatus='X',
                            pres_fecha_devolucion__isnull=True,
                            pres_folio__usua_clave=usuario
                        ).values_list('vide_codigo__pk', flat=True)

                        if codigoBarras in cintas_pendientes:
                            registro_data = {
                                "error": True,
                                "errorMessage": "El usuario debe devolver todas las cintas pendientes antes de solicitar un nuevo préstamo",
                                "cintasPendientes": list(cintas_pendientes)
                            }
                        else:
                            registro_data = {
                                "error": False,
                                "successMessage": "Listo para préstamo"
                            }

                else:
                    registro_data = {
                        "error": True,
                        "errorMessage": "El código de barras no está disponible",
                        'codigoBarras': codigoBarras
                    }
            except MaestroCintas.DoesNotExist:
                registro_data = {
                    "error": True,
                    "errorMessage": "No se encontró el código de barras"
                }
    else:
        registro_data = {
            "error": True,
            "errorMessage": "Solicitud inválida"
        }

    return JsonResponse(registro_data)




@csrf_exempt      
def RegisterOutVideoteca(request):

    now = datetime.now()

    if request.method == 'POST':
        usuario = request.POST['usuario']
        admin = request.user
        data = json.loads(request.POST['codigos'])

        prestamo = Prestamos()
        prestamo.usua_clave = usuario
        prestamo.usvi_clave = admin 
        prestamo.pres_fechahora = now
        prestamo.pres_fecha_prestamo = now
        prestamo.pres_fecha_devolucion = None
        # prestamo.pres_fecha_devolucion = now + timedelta(days=7)
        prestamo.pres_estatus = 'X'
        prestamo.save()

        pintaFolio = prestamo.pres_folio
        
        for codigo in data:
            try:
                maestroCinta = MaestroCintas.objects.get(pk=codigo)
            except MaestroCintas.DoesNotExist:
                return JsonResponse({'error': True, 'errorMessage': 'No se encontró el código de barras'}, safe=True)

            detPrestamos = DetallePrestamos()
            detPrestamos.pres_folio = prestamo
            detPrestamos.depr_estatus = 'X'
            detPrestamos.pres_fecha_devolucion = None
            detPrestamos.usuario_devuelve = None
            detPrestamos.usuario_recibe = None
            detPrestamos.vide_codigo = maestroCinta
            detPrestamos.save()
    

            maestroCinta.video_estatus = 'X'
            maestroCinta.save()

        registro_data = {"error": False, "errorMessage": "Listo para préstamo", 'Folio': pintaFolio}
        return JsonResponse(registro_data, safe=True)

    return JsonResponse({}, safe=True)

@csrf_exempt   
def EndInVideoteca(request):
    usuario = request.POST.get('usuario')
    data = request.POST.get('codigos') 

    from django.db import connections
    cursor = connections['users'].cursor()
    cursor.execute("select a.nombres, a.apellido1, a.apellido2, a.extension_telefonica, a.email_institucional, b.nombre as Area, c.nombre as contratacion, a.activo from people_person as a join people_areaorganigrama as b  on a.cat_area_org_id = b.id  join people_contratacion as c on a.cat_contratacion_id = c.id where a.matricula = %s", [usuario])

    row = cursor.fetchall()
    if row:
        file = json_to_pdf(request, row, data, usuario)
        if file:
            registro_data = {"error": False, "file": file}
        else:
            registro_data = {"error": True, "errorMessage": "Error al generar archivo de devolución"}
    else:
        registro_data = {"error": True, "errorMessage": "No se encontraron registros para el usuario"}

    return JsonResponse(registro_data, safe=True)

