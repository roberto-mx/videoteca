from django.views.generic import ListView
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from ..forms import PrestamoInlineFormset
from .reports import json_to_pdf
from django.shortcuts import render
from functools import reduce
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import textwrap, operator, base64, json, datetime
from django.template.loader import get_template
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404
import tempfile
import os
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

# def Filtrar_pres_Folio(request):
#     q = request.GET.get('q')

#     # Obtener los pres_folio que coinciden con el vide_codigo
#     pres_folios = DetallePrestamos.objects.filter(pres_folio_id=q).values_list('pres_folio_id', flat=True)

#     # Crear una lista para almacenar los datos de prestamos
#     prestamos_data = []

#     # Obtener los datos de Prestamos para cada pres_folio encontrado
#     for pres_folio_id in pres_folios:
#         prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
#         if prestamo:
#             # Acceder a los datos de Prestamos
#             prestamo_data = {
#                 "pres_folio": prestamo.pres_folio,
#                 "usua_clave": prestamo.usua_clave,
#                 "pres_fechahora": prestamo.pres_fechahora,  
#                 "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
#                 "pres_estatus": prestamo.pres_estatus
#             }
            
#             prestamos_data.append(prestamo_data)

#     # Retornar los datos de prestamos en formato JSON
#     return JsonResponse(prestamos_data, safe=False)

@method_decorator(login_required, name='dispatch')
class PrestamosListView(ListView):
    def get(self, request):
        queryset = Prestamos.objects.filter(Q(pres_fecha_prestamo__year='2022')).order_by('-pres_fechahora')
        context = {
            'prestamos': queryset,
        }
        return render(request, 'prestamos/prestamos_list.html', context)
    

@csrf_exempt
def PrestamoDetalle(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion')
    context = { 'detalles': queryset }
    return render(request, 'prestamos/prestamos_detalle_list.html', context)

    # q = int(request.GET.get("q"))
    # queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion')
    # prestamo = list(queryset)  # convertimos el queryset en una lista
    # return JsonResponse({'prestamo': prestamo})



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

    #list = []  
    #for comp in querysetComp:
        #consulta=Compensaciones.objects.filter(Q(compensacion = comp))
       # list.append(CompToShow(comp.nombre + " (" + str(comp.numero -consulta.count()) +")", comp.pk ))    

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
    #videoDetail = MaestroCintas.objects.get(video_id =detailPrestamo.vide_clave )
    # programaDetail = DetalleProgramas.objects.filter(video_cbarras=videoDetail.video_cbarras)
    t = get_template('prestamos/detalle_prestamos.html')
    content = t.render(
    {
        #'cintas': videoDetail, 
        'detalles' : detailPrestamo,
          
    })
    return HttpResponse(content)



@csrf_exempt      
def RegisterInVideoteca(request):
    # usuario = request.POST['matricula']
    # admin = request.user
    # from django.db import connections
    # cursor = connections['users'].cursor()
    # cursor.execute("select nombres, apellido1, apellido2, activo from people_person where matricula = '"+ usuario + "'")
    # row = cursor.fetchall()
    # print(row[0][3])    
    if request.method == 'POST':
        print(request.POST['codigoBarras'])
        now = datetime.datetime(2022, 12, 29, 00, 00, 00, 0) 
        #datetime.datetime.now()
        codigoBarras = request.POST['codigoBarras']
        try:
            error="Código no encontrado"
            maestroCinta = MaestroCintas.objects.get(pk = codigoBarras)
            error= "Busqueda en Maestro Cintas"
           
            error= "Busqueda en Videos"
            detallesPrestamo = DetallePrestamos.objects.filter( Q(vide_clave = maestroCinta.video_id) )
            detallesPrestamoMaster = DetallePrestamos.objects.filter(Q(vide_codigo = codigoBarras ))
            #& Q(depr_estatus ='A')
            error= "No se encontro en Prestamos"
            if detallesPrestamo.count() > 0:
                detallePrestamo = detallesPrestamo.latest('pres_folio')
            elif detallesPrestamoMaster.count() > 0:
                detallePrestamo = detallesPrestamoMaster.latest('pres_folio')
            else:
                print("Hay que revisar los registros de esté codigo de barras")
                registro_data={"error": True, "errorMessage":"Hay que revisar los registros de esté codigo de barras"}
                return JsonResponse(registro_data,safe=True)
            
            prestamo = Prestamos.objects.get(pres_folio= detallePrestamo.pres_folio_id)

            detallePrestamo.depr_estatus='I'
            detallePrestamo.pres_fecha_devolucion = now
            # detallePrestamo.usuario_devuelve = usuario
            detallePrestamo.usuario_recibe = 'M090077'
            detallePrestamo.save()
            maestroCinta.video_estatus='En Videoteca'
            maestroCinta.save()

            prestamosActivos = DetallePrestamos.objects.filter(Q(pres_folio_id = prestamo.pk) & Q(depr_estatus ='A'))
            if prestamosActivos.count == 0:
                #VALIDAR SI AUN HAY PRESTAMOS ACTIVOS 
                prestamo.pres_estatus ='I'
                prestamo.pres_fecha_devolucion = now
                prestamo.save()

            registro_data={"error":False,"errorMessage":" Registro Exitoso!"}
        except Exception as e:
            registro_data={"error":True,"errorMessage":" No se dio de alta correctamente el reingreso: "+ error}
           
    return JsonResponse(registro_data,safe=True)
# def RegisterInVideoteca(request):
#     usuario = request.POST['matricula']
#     admin = request.user
#     from django.db import connections
#     cursor = connections['users'].cursor()
#     cursor.execute("SELECT nombres, apellido1, apellido2, activo FROM people_person WHERE matricula = '"+ usuario + "'")
#     row = cursor.fetchall()
#     if row and len(row[0]) > 3:
#         print(row[0][3])    
#     if request.method == 'POST':
#         print(request.POST['codigoBarras'])
#         now = datetime.datetime(2022, 12, 29, 00, 00, 00, 0) 
#         #datetime.datetime.now()
#         codigoBarras = request.POST['codigoBarras']
#         try:
#             error = "Código no encontrado"
#             maestroCinta = MaestroCintas.objects.get(pk=codigoBarras)
#             error = "Búsqueda en Maestro Cintas"
           
#             error = "Búsqueda en Videos"
#             detallesPrestamo = DetallePrestamos.objects.filter(Q(vide_clave=maestroCinta.video_id))
#             detallesPrestamoMaster = DetallePrestamos.objects.filter(Q(vide_codigo=codigoBarras))
#             error = "No se encontró en Prestamos"
#             if detallesPrestamo.count() > 0:
#                 detallePrestamo = detallesPrestamo.latest('pres_folio')
#             elif detallesPrestamoMaster.count() > 0:
#                 detallePrestamo = detallesPrestamoMaster.latest('pres_folio')
#             else:
#                 print("Hay que revisar los registros de este código de barras")
#                 registro_data = {"error": True, "errorMessage": "Hay que revisar los registros de este código de barras"}
#                 return JsonResponse(registro_data, safe=True)
            
#             # Validar si ya ha sido devuelto
#             if detallePrestamo.depr_estatus == 'I':
#                 registro_data = {"error": True, "errorMessage": "El código de barras ya ha sido devuelto"}
#                 return JsonResponse(registro_data, safe=True)

#             prestamo = Prestamos.objects.get(pres_folio=detallePrestamo.pres_folio_id)

#             detallePrestamo.depr_estatus = 'I'
#             detallePrestamo.pres_fecha_devolucion = now
#             detallePrestamo.usuario_devuelve = usuario
#             detallePrestamo.usuario_recibe = admin.username
#             detallePrestamo.save()
#             maestroCinta.video_estatus = 'En Videoteca'
#             maestroCinta.save()

#             prestamosActivos = DetallePrestamos.objects.filter(Q(pres_folio_id=prestamo.pk) & Q(depr_estatus='A'))
#             if prestamosActivos.count == 0:
#                 # VALIDAR SI AUN HAY PRESTAMOS ACTIVOS 
#                 prestamo.pres_estatus = 'I'
#                 prestamo.pres_fecha_devolucion = now
#                 prestamo.save()

#             registro_data = {"error": False, "errorMessage": "Registro Exitoso!"}
#         except Exception as e:
#             registro_data = {"error": True, "errorMessage": "No se dio de alta correctamente el reingreso: " + error}
           

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
                    registro_data = {
                        "error": False,
                        "errorMessage": "Listo para préstamo"
                    }
                    # Guardar el registro en la base de datos aquí
                else:
                    registro_data = {
                        "error": True,
                        "errorMessage": "El código de barras no está disponible"
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
    now = datetime.datetime.now()

    if request.method == 'POST':
        usuario = request.POST['usuario']
        data = json.loads(request.POST['codigos'])
        prestamo = Prestamos()
        prestamo.usua_clave = usuario
        prestamo.pres_fechahora = now
        prestamo.pres_fecha_prestamo = now
        prestamo.pres_fecha_devolucion = now
        prestamo.pres_estatus = 'X'
        prestamo.save()

        
        pintaFolio = prestamo.pres_folio
        print(pintaFolio)

        for codigo in data:
            try:
                maestroCinta = MaestroCintas.objects.get(pk=codigo)
            except MaestroCintas.DoesNotExist:
                return JsonResponse({'error': True, 'errorMessage': 'No se encontró el código de barras'}, safe=True)

            detPrestamos = DetallePrestamos()
            detPrestamos.pres_folio = prestamo
            detPrestamos.depr_estatus = 'X'
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

# def EndInVideoteca(request):
#     usuario = request.POST.get('usuario')
#     data = request.POST.get('codigos')
    
#     from django.db import connections
#     cursor = connections['users'].cursor()
#     cursor.execute("select a.nombres, a.apellido1, a.apellido2, a.extension_telefonica, a.email_institucional, b.nombre as Area, c.nombre as contratacion, a.activo from people_person as a join people_areaorganigrama as b  on a.cat_area_org_id = b.id  join people_contratacion as c on a.cat_contratacion_id = c.id where a.matricula = %s", [usuario])
    
#     row = cursor.fetchall()
#     if row:
#         print(row[0][3])
#         file = json_to_pdf(request, row, data, usuario)
#         if file:
#             registro_data = {"error": False, "file": file}
#         else:
#             registro_data = {"error": True, "errorMessage": "Error al generar archivo de devolución"}
#     else:
#         registro_data = {"error": True, "errorMessage": "No se encontraron registros para el usuario"}
    
#     return JsonResponse(registro_data, safe=True)