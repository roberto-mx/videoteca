from django.views.generic import ListView
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from ..forms import PrestamoInlineFormset
from django.shortcuts import render
from functools import reduce
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import textwrap, operator, base64, json, datetime
from django.template.loader import get_template
from django.db.models import Q
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
    # ---------------------------
    # Prestamos
    # ---------------------------

@method_decorator(login_required, name='dispatch')
class PrestamosListView(ListView):
    model = Prestamos
    template_name = 'prestamos/prestamos_list.html'
    def get(self, request, *args, **kwargs):
        
        #queryset =DetallePrestamos.objects.filter(Q(pres_folio__pres_fecha_prestamo__year = '2022')).order_by('-pres_folio__pres_fechahora')
        queryset = Prestamos.objects.filter(Q(pres_fecha_prestamo__year = '2022')).order_by('-pres_fechahora')
        #list = []  
        #for comp in querysetComp:
         #   consulta=Compensaciones.objects.filter(Q(compensacion = comp))
         #   list.append(CompToShow(comp.nombre + " (" + str(comp.numero -consulta.count()) +")", comp.pk ))
        content = {#t.render(
            'prestamos': queryset, 
         #   'compensacion' : list,
        }#)
        return render(request, 'prestamos/prestamos_list.html' , content)    
    

@csrf_exempt
   
def PrestamoDetalle(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion')
    context = {'detalles': queryset}
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
            #& Q(depr_estatus ='A')
            error= "No se encontro en Prestamos"
            if detallesPrestamo.count() > 0:
                detallePrestamo = detallesPrestamo.latest('pres_folio')
                prestamo = Prestamos.objects.get(pres_folio= detallePrestamo.pres_folio_id)
            else:
                print("Hay que revisar los registros de esté codigo de barras")
                registro_data={"error": True, "errorMessage":"Hay que revisar los registros de esté codigo de barras"}
                return JsonResponse(registro_data,safe=True)
            
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

            registro_data={"error":False,"errorMessage":"Registro Exitoso!"}
        except Exception as e:
            registro_data={"error":True,"errorMessage":"No se dio de alta correctamente el reingreso: "+ error}
           
    return JsonResponse(registro_data,safe=True)

@csrf_exempt  
def ValidateOutVideoteca(request):
    if request.method == 'POST':
        print(request.POST['codigoBarras'])
        codigoBarras = request.POST['codigoBarras']
        try:
            maestroCinta = MaestroCintas.objects.get(pk = codigoBarras)
            if maestroCinta.video_estatus =='En Videoteca':
                registro_data={"error":False,"errorMessage":"Listo para prestamo"}
            else:
                registro_data={"error":True,"errorMessage":"El material solicitado se encuentra registrado con estatus: " + maestroCinta.video_estatus}
        except Exception as e:
            registro_data={"error":True,"errorMessage":"No se encontro el codigo de barras"}    
    return JsonResponse(registro_data,safe=True)


@csrf_exempt      
def RegisterOutVideoteca(request):
    now = datetime.datetime.now()
    if request.method == 'POST':
        usuario = request.POST['usuario']
        data = json.loads(request.POST['codigos'])
        for codigo in data:
            maestroCinta = MaestroCintas.objects.get(pk = codigo)

            prestamo = Prestamos()
            prestamo.usua_clave = usuario
            prestamo.pres_fechahora = now
            prestamo.pres_fecha_prestamo = now
            prestamo.pres_fecha_devolucion = now
            prestamo.pres_estatus = 'X'
            prestamo.save()

            detPrestamos = DetallePrestamos()
            detPrestamos.pres_folio = prestamo
            # detPrestamos.vide_clave = videos
            detPrestamos.depr_estatus = 'X'
            detPrestamos.save()

            maestroCinta.video_estatus = 'X'
            maestroCinta.save()

        registro_data={"error":True,"errorMessage":"No se encontro el codigo de barras"}    
    return JsonResponse(registro_data,safe=True)
    