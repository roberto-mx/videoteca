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
from django.db.models import F
from django.http import JsonResponse
from django.core import serializers
from fpdf import FPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.shortcuts import get_object_or_404
import tempfile


    # ---------------------------
    # Prestamos
    # ---------------------------

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

def Filtrar_prestamos(request):
    q = request.GET.get('q')

    # Obtener los pres_folio que coinciden con el vide_codigo
    pres_folios = DetallePrestamos.objects.filter(vide_codigo_id=q).values_list('pres_folio_id', flat=True)

    # Crear una lista para almacenar los datos de prestamos
    prestamos_data = []

    # Obtener los datos de Prestamos para cada pres_folio encontrado
    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        if prestamo:
            # Acceder a los datos de Prestamos
            prestamo_data = {
                "pres_folio": prestamo.pres_folio,
                "usua_clave": prestamo.usua_clave,
                "pres_fechahora": prestamo.pres_fechahora,  
                "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                "pres_estatus": prestamo.pres_estatus
            }
            
            prestamos_data.append(prestamo_data)

    # Retornar los datos de prestamos en formato JSON
    return JsonResponse(prestamos_data, safe=False)

# ---------------------------------------------------------------------------------------------------------------------------#

class PDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        self.q = q

    def header(self):
        
        # Configuración de la cabecera del PDF
        self.image('images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Arial', 'B', 8)
        self.cell(480,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(518,1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(458,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(40)

        self.set_font('Arial', 'B', 8)
        self.cell(84, 10,   'NOMBRE:      _______________________________', 0, 0, 'C')
        # self.ln(7)
        self.cell(306, 10,  'DIRECCIÓN:   _______________________________', 0, 0, 'C')
        self.ln(17)
        self.cell(83, 10,   'PUESTO:      _______________________________', 0, 0, 'C')

        self.cell(103, 10,  'EXTENSIÓN:   _______________________________', 0, 0, 'C')
        self.cell(103, 10,  'CORREO:      _______________________________', 0, 0, 'C')
        self.ln(40)
        
        self.set_font('Arial', 'B', 15)
        self.cell(280, 10, f'Prestamos de la cinta ({self.q})', 0, 0, 'C')
        self.ln(20)
        
    def footer(self):

        self.ln(40)
        self.set_font('Arial', 'B', 8)
        self.cell(103, 10, 'RECIBE:', 0, 0, 'C')
        self.cell(200, 10, 'DEVUELVE:', 0, 0, 'C')
        self.ln()

        self.cell(103, 10, '________________________________________', 0, 0, 'C')
        # self.ln(8)
        self.cell(200, 10, '________________________________________', 0, 0, 'C')
        # self.ln()

        # Configuración del pie de página del PDF
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_table(self, data):
        # Generación del contenido de la tabla en el PDF
        self.set_fill_color(144, 12, 63)
        self.set_text_color(255, 255, 255) # Establece el color de la letra en blanco
        self.cell(40, 10, 'Folio', 1, 0, '', True)
        self.cell(40, 10, 'Usuario', 1, 0, '', True)
        self.cell(80, 10, 'Fecha y Hora Prestamo', 1, 0, '', True)
        self.cell(80, 10, 'Fecha de devolución', 1, 0, '', True)
        self.cell(40, 10, 'Estatus', 1, 0, '', True)
        self.set_text_color(0, 0, 0)
        self.ln()

        for row in data:
            self.cell(40, 10, str(row['pres_folio']), 1)
            self.cell(40, 10, str(row['usua_clave']), 1)
            self.cell(80, 10, str(row['pres_fechahora']), 1)
            self.cell(80, 10, str(row['pres_fecha_devolucion']), 1)
            self.cell(40, 10, str(row['pres_estatus']), 1)
            self.ln()

def generar_pdf(request):
    q = request.GET.get('q')
    detalle_prestamos = DetallePrestamos.objects.filter(vide_codigo=q)
    pres_folios = detalle_prestamos.values_list('pres_folio_id', flat=True)
    prestamos_data = []
    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        if prestamo:
            prestamo_data = {
                "pres_folio": prestamo.pres_folio,
                "usua_clave": prestamo.usua_clave,
                "pres_fechahora": prestamo.pres_fechahora,
                "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                "pres_estatus": prestamo.pres_estatus
            }
            prestamos_data.append(prestamo_data)

    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="Videoteca.pdf"'
    response['Content-Disposition'] = f'attachment; filename="Videoteca_{q}.pdf"'
    pdf = PDF('P', 'mm', (300, 350), q)

    # Abre una nueva página en el documento PDF
    pdf.add_page()

    # Agrega los datos de los préstamos a la página actual
    pdf.generate_table(prestamos_data)
    

    response.write(pdf.output(dest='S').encode('latin1'))
    return response





# ---------------------------------------------------------------------------------------------------------------------------#

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
    