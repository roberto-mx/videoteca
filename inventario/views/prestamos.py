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
import tempfile
import os
from django.views import View
from django.db import connections
from datetime import datetime
# from businesstimedelta import Businesstimedelta

# from django.utils import timezone
from datetime import datetime, timedelta, date
# from django.utils import timezone
from django.db import connections

def Filtrar_prestamos(request):
    q = request.GET.get('q')

    prestamos_data = []

    if q:
        try:
            q = str(q)  # Convertir a número entero
            prestamos = DetallePrestamos.objects.filter(
                Q(pres_folio=q) | Q(vide_codigo=q) | Q(pres_folio__usua_clave=q)
            )

            usuarios_dict = obtener_usuarios_dict(prestamos)

            for prestamo in prestamos:
                nombre_completo  = usuarios_dict.get(prestamo.pres_folio.usua_clave, "Nombre no encontrado")
                estatus = "En préstamo" if prestamo.pres_folio.pres_estatus == 'X' else "En Videoteca" 

                prestamo_data = {
                    "pres_folio": prestamo.pres_folio.pres_folio,
                    "usua_clave": prestamo.pres_folio.usua_clave,
                    "pres_fechahora": prestamo.pres_folio.pres_fechahora,
                    "pres_fecha_devolucion": prestamo.pres_folio.pres_fecha_devolucion,
                    "pres_estatus": estatus,
                    "usuario": {
                        "matricula": prestamo.pres_folio.usua_clave,
                        "nombre_completo": nombre_completo,
                    }
                }
                prestamos_data.append(prestamo_data)

        except ValueError:
            pass

    return JsonResponse(prestamos_data, safe=False)

def obtener_usuarios_dict(prestamos):
    matriculas_list = [prestamo.pres_folio.usua_clave for prestamo in prestamos]
    
    cursor = connections['users'].cursor()

    if matriculas_list:
        cursor.execute("SELECT matricula, nombres, apellido1, apellido2 FROM people_person WHERE matricula IN %s", (tuple(matriculas_list),))
        users_data = cursor.fetchall()
    else:
        users_data = []

    # Crear un diccionario para mapear matrículas a nombres completos
    usuarios_dict = {row[0]: f"{row[1]} {row[2]} {row[3]}" if row[3] else f"{row[1]} {row[2]}" for row in users_data}

    return usuarios_dict

@method_decorator(login_required, name='dispatch')
class PrestamosListView(View):
    template_name = 'prestamos/prestamos_list.html'

    def get(self, request, *args, **kwargs):
        current_year = datetime.now().year

        # Obtener los préstamos filtrados por el año 2023 y ordenados por fecha en orden descendente
        queryset = Prestamos.objects.filter(pres_fecha_prestamo__year__gte=2023).order_by('-pres_fecha_prestamo')

        # Obtener las matrículas
        matriculas = queryset.values_list('usua_clave', flat=True)
        matriculas_list = list(matriculas)

        context = {'prestamos': queryset}
        print(context)

        if matriculas_list:
            cursor = connections['users'].cursor()
            cursor.execute("SELECT matricula, nombres, apellido1, apellido2 FROM people_person WHERE matricula IN %s", (tuple(matriculas_list),))
            users_data = cursor.fetchall()

            # Crear una lista de usuarios en el contexto
            context['usuarios'] = []

            for row in users_data:
                matricula, nombres, apellido1, apellido2 = row
                nombre_completo = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"

                # Agregar la información del usuario a la lista de usuarios en el contexto
                context['usuarios'].append({
                    'matricula': matricula,
                    'nombre_completo': nombre_completo,
                })

        return render(request, self.template_name, context)

@csrf_exempt
def DetallesListView(request):
    a = request.GET.get('a')

    # Obtener la información del préstamo
    prestamo = Prestamos.objects.filter(pres_folio=a).values('pres_fecha_prestamo', 'pres_estatus', 'usua_clave').first()

    if prestamo is not None:
        matricula = prestamo['usua_clave']
        cursor = connections['users'].cursor()
        cursor.execute("SELECT matricula, nombres, apellido1, apellido2 FROM people_person WHERE matricula = %s", (matricula,))
        users_data = cursor.fetchall()

        if users_data:
            row = users_data[0]
            nombre_completo = f"{row[1]} {row[2]} {row[3]}" if row[3] else f"{row[1]} {row[2]}"
        else:
            nombre_completo = "Nombre no encontrado"
    else:
        nombre_completo = "Nombre no encontrado"

    fecha_prestamo = prestamo['pres_fecha_prestamo'].date() if prestamo else None
    estatusPrestamo = prestamo['pres_estatus'] if prestamo else None

    dias_habiles_encontrados = 0
    desplazamiento = timedelta(days=1)

    fecha_actual = fecha_prestamo if fecha_prestamo else None

    while fecha_actual and dias_habiles_encontrados < 7:
        # Calcular la fecha de vencimiento sumando 1 día a la vez
        fecha_actual += desplazamiento
        
        # Verificar si la fecha actual es un día hábil (de lunes a viernes)
        if fecha_actual.weekday() < 5:
            dias_habiles_encontrados += 1

    fecha_vencimiento = fecha_actual.strftime('%d-%m-%Y') if fecha_actual else None

    template_detalle = {
        'vencioElDia': fecha_vencimiento,
        'estatusPrestamo': estatusPrestamo,
        'nombreCompleto': nombre_completo
    }

    print(template_detalle['nombreCompleto'])

    return JsonResponse(template_detalle, safe=False)

@csrf_exempt
def obtenerPeoplePerson(request):
    fecha_actual = datetime.now().date()
    fecha_actual_formato = fecha_actual.strftime('%d-%m-%Y')
    hace_siete_dias = fecha_actual - timedelta(days=7)

    q = request.GET.get('q')
    prestamo = Prestamos.objects.filter(pres_folio=q).values('usua_clave', 'pres_fecha_prestamo').first()

    matri = None
    if prestamo is not None:
        matri = prestamo['usua_clave']
        fechaPrestamo = prestamo['pres_fecha_prestamo'].strftime('%d-%m-%Y')

    if matri is not None:
        cursor = connections['users'].cursor()
        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [matri])

        row = cursor.fetchone()

        MatriculaObPrestamo = {}

        if row is not None:
            nombres = row[0]
            apellido1 = row[1]
            apellido2 = row[2]
            puesto = row[3]
            email_institucional = row[4]
            extension_telefonica = row[5]

            nombre_completo = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
            MatriculaObPrestamo = {
                'Obtiene': nombre_completo,
                'Puesto': puesto,
                'Email': email_institucional,
                'Extension': extension_telefonica,
                'Matricula': matri,
                'PrestamoFecha': fechaPrestamo,
                'fechaActual': fecha_actual_formato,
                'tiempoDevolucion': hace_siete_dias,
            }

    # Respuesta JSON movida al final de la vista
    return JsonResponse(MatriculaObPrestamo, safe=False)

@csrf_exempt
def PrestamoDetalle(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values(
        'vide_codigo_id',
        'pres_fecha_devolucion',
        'usuario_devuelve',
        'usuario_recibe',
        'depr_estatus',
    )

    usuarios_name = obtener_usuarios_name(queryset)

    for detalle in queryset:
        detalle['nombre_completo_devuelve'] = usuarios_name.get(detalle['usuario_devuelve'], "Nombre no encontrado")
        detalle['nombre_completo_recibe'] = usuarios_name.get(detalle['usuario_recibe'], "Nombre no encontrado")

    context = { 'detalles': queryset }
    return render(request, 'prestamos/prestamos_detalle_list.html', context)

def obtener_usuarios_name(queryset):
    
    usua_claves = set()
    for detalle in queryset:
        usua_claves.add(detalle['usuario_devuelve'])
        usua_claves.add(detalle['usuario_recibe'])

    # Filtra las claves que no son None
    usua_claves = [claves for claves in usua_claves if claves is not None]

    # Consulta la base de datos para obtener los nombres completos de los usuarios
    cursor = connections['users'].cursor()
    if usua_claves:
        cursor.execute("SELECT matricula, nombres, apellido1, apellido2 FROM people_person WHERE matricula IN %s", (tuple(usua_claves),))
        users_data = cursor.fetchall()
    else:
        users_data = []

    # Crea un diccionario para mapear matrículas a nombres completos
    usuarios_name = {row[0]: f"{row[1]} {row[2]} {row[3]}" if row[3] else f"{row[1]} {row[2]}" for row in users_data}

    return usuarios_name

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
    # admin = request.user

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
            # detallePrestamo.usuario_recibe = usuario
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
                         
                    ).values('pres_folio').distinct()  # Obtengo el valor del Folio a través del modelo

                    print('foliosVenncidos',folios_vencidos)

                    for folio in folios_vencidos:
                        cintas_pendientes = DetallePrestamos.objects.filter(
                            pres_folio_id=folio['pres_folio'],
                            depr_estatus='X'
                        ).values_list('vide_codigo_id', flat=True)

                        cintas_faltantes = list(set(cintas_pendientes) - set([codigoBarras]))
                
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
                                "successMessage": "Listo para préstamo",
                                "fechaVencimiento": fecha_vencimiento
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
            detPrestamos.usuario_recibe = usuario
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


@csrf_exempt
def getBusqueda(request):
    if request.method == 'GET':
        searchType = request.GET.get('searchType', None)
        day = request.GET.get('day', None)
        week = request.GET.get('week', None)
        month = request.GET.get('month', None)
        template_name = 'prestamos/consultPorFecha.html'

        if searchType == 'byDay' and day:
            # Búsqueda por día
            day_datetime = datetime.strptime(day, "%Y-%m-%d")
            prestamos = Prestamos.objects.filter(pres_fecha_prestamo__date=day_datetime)
            prestamos_list = list(prestamos.values())

            # Acceder a la información de usua_clave en cada registro
            matriculas_list = [prestamo['usua_clave'] for prestamo in prestamos_list]
            cursor = connections['users'].cursor()

            if matriculas_list:
                cursor.execute("SELECT matricula, nombres, apellido1, apellido2 FROM people_person WHERE matricula IN %s", (tuple(matriculas_list),))
                users_data = cursor.fetchall()
            else:
                users_data = []

            usuarios_dict = {row[0]: f"{row[1]} {row[2]} {row[3]}" if row[3] else f"{row[1]} {row[2]}" for row in users_data}        
           
                # Actualizar cada diccionario en prestamos_list con el nombre del usuario
            for prestamo in prestamos_list:
                matricula = prestamo['usua_clave']
                nombreUsuario = usuarios_dict.get(matricula, '')
                prestamo['nombre_usuario'] = nombreUsuario

            registro_data = {"error": False, "errorMessage": "Listo", 'prestamos': prestamos_list}
            return JsonResponse(registro_data, safe=False)

        elif searchType == 'byWeek' and week:
            # Descomponer la cadena de semana en año y número de semana
            year, week_number = map(int, week.split('-W'))

            # Obtener el primer día de la semana
            inicio_semana = datetime.strptime(f"{year}-W{week_number}-1", "%Y-W%W-%w").date()

            # Obtener el último día de la semana sumando 6 días al primer día
            fin_semana = inicio_semana + timedelta(days=6)

            # Filtrar por el rango de fechas
            queryset = Prestamos.objects.filter(pres_fecha_prestamo__range=(inicio_semana, fin_semana)).order_by('-pres_fecha_prestamo')
            prestamos_list = list(queryset.values())
            print(prestamos_list)

            registro_data = {"error": False, "errorMessage": "Listo", 'prestamos': prestamos_list}
            return JsonResponse(registro_data, safe=False)
                    
        elif searchType == 'byMonth' and month:
            print('Entra en mes', month)
            # Extraer el año y el mes de la cadena proporcionada
            year, month_number = map(int, month.split('-'))
            # Filtrar por año y mes
            queryset = Prestamos.objects.filter(
                pres_fecha_prestamo__year__gte=year,
                pres_fecha_prestamo__month__gte=month_number
            ).order_by('-pres_fecha_prestamo')
            prestamos_list = list(queryset.values())
            print(prestamos_list)
            
            print(queryset)
            registro_data = {"error": False, "errorMessage": "Listo", 'prestamos': prestamos_list}
            return JsonResponse(registro_data, safe=False)

    return render(request, template_name)

