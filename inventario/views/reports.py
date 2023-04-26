import textwrap, operator, base64, json, datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# from pyreportjasper import PyReportJasper
from django.core import serializers
from fpdf import FPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from django.http.response import HttpResponse, JsonResponse
import os 
import io
from django.db.models import Q
from PyPDF2 import PdfWriter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter, landscape
from django.db import connections
import json
from django.http import JsonResponse
from django.db import connections


@csrf_exempt
def ejemplo(request):
    matricula = request.GET.get('matricula')
    detalle_matricula = DetallePrestamos.objects.filter(usuario_devuelve=matricula).first()
    muestraData = []

    if detalle_matricula is not None:
        matricula_data = {
            "UsuarioDevuelve": detalle_matricula.usuario_devuelve,
            "UsuarioRecibe"  : detalle_matricula.usuario_recibe
        }
        muestraData.append(matricula_data)
        if muestraData:
            usuario_devuelve = muestraData[0]["UsuarioDevuelve"]
            usuario_recibe = muestraData[0]["UsuarioRecibe"]

    cursor = connections['users'].cursor()
    cursor.execute("select nombres, apellido1, apellido2, activo from people_person where matricula = %s", [usuario_devuelve])
    row = cursor.fetchone()

    if row is not None:
        nombres   = row[0]
        apellido1 = row[1]
        apellido2 = row[2]
        activo    = row[3]

        MatriculaDevuelve = {
            'Nombres'           : nombres,
            'ApellidoPaterno'   : apellido1,
            'ApellidoMaterno'   : apellido2,
            'EstatusActivo'     : activo,
            'Matricula'         : usuario_devuelve,
        }

    cursor.execute("select nombres, apellido1, apellido2, activo from people_person where matricula = %s", [usuario_recibe])
    row = cursor.fetchone()

    if row is not None:
        nombres   = row[0]
        apellido1 = row[1]
        apellido2 = row[2]
        activo    = row[3]

        MatriculaRecibe = {
            'Matricula'         : usuario_recibe,
            'Nombres'           : nombres   if nombres   else '',
            'Apellido'          : apellido1 if apellido1 else '',
            'Apellido2'         : apellido2 if apellido2 else '',
            'Activo'            : activo    if activo    else '',
        }   
        
        response_data = {
            'UsuarioDevuelve': MatriculaDevuelve,
            'UsuarioRecibe'   : MatriculaRecibe
        }
        return JsonResponse(response_data, safe=False)
    
class PDF(FPDF):
    def __init__(self,request, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        self.q = q
        self.request = request


    def header(self):
        # matricula         = self.request.GET.get('matricula')
        # response_data     = ejemplo(self.request)
        # MatriculaDevuelve = response_data['MatriculaDevuelve']
        # MatriculaRecibe   = response_data['MatriculaRecibe']
        
        # Configuración de la cabecera del PDF
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=65)
        self.image('media/images/logo-aprendemx.png', x=76, y=5, w=65)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(485,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(525,1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(458,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(10)

        self.cell(84, 10, 'NOMBRE:', 0, 0, 'L')
       
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 65, y + 5)  
        self.ln(7) 

        self.cell(84, 10, 'Dirección:', 0, 0, 'L')
        
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 65, y + 5) 
        self.ln(7)

        self.cell(84, 10, 'Correo:', 0, 0, 'L')
        
        x = self.get_x()
        y = self.get_y()
        
        self.line(x - 65, y + 5, x + 65, y + 5)  
        self.ln(7)

        self.cell(84, 10, 'Puesto:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        
        self.line(x - 65, y + 5, x + 10, y + 5)  
        self.ln(7)

        self.cell(84, 10, 'Extención:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 10, y + 5)      
        self.ln(15)
        
        self.set_font('Montserrat', 'B', 8)
        self.cell(280, 10, f'Prestamos de la cinta ({self.q})', 0, 0, 'C')
        self.ln(15)

        self.set_fill_color(144, 12, 63)
        self.set_text_color(255, 255, 255) 
        self.cell(40, 10, 'Folio', 1, 0, '', True)
        self.cell(40, 10, 'Usuario', 1, 0, '', True)
        self.cell(80, 10, 'Fecha y Hora Prestamo', 1, 0, '', True)
        self.cell(80, 10, 'Fecha de devolución', 1, 0, '', True)
        self.cell(40, 10, 'Estatus', 1, 0, '', True)
        self.set_text_color(0, 0, 0)
        self.ln()
        
    def footer(self):

        self.ln(10)
        self.set_font('Montserrat', 'B', 8)

        self.cell(84, 10, 'Devuelve:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 10, y + 5)      
        self.ln(7)

        self.cell(84, 10, 'Recibe:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 10, y + 5)      
        self.ln()
        

        # Configuración del pie de página del PDF
        self.set_y(-15)
        self.set_font('Montserrat', '', 8)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_table(self, data):
       
        for row in data:
            self.cell(40, 10, str(row['pres_folio']), 1)
            self.cell(40, 10, str(row['usua_clave']), 1)
            self.cell(80, 10, str(row['pres_fechahora']), 1)
            self.cell(80, 10, str(row['pres_fecha_devolucion']), 1)
            self.cell(40, 10, str(row['pres_estatus']), 1)
            self.ln()

def generar_pdf(request):
    q = request.GET.get('q')
    detalle_prestamos = DetallePrestamos.objects.filter(Q(vide_codigo=q) | Q(pres_folio__pres_folio=q))
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
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = PDF('P', 'mm', (300, 350), q)
    pdf.add_font('Montserrat','',
            r"C:\Users\MIJIMENEZ\Desktop\videoteca\media\static\Montserrat-Regular.ttf",
            uni=True)
    pdf.add_font('Montserrat','B',
            r"C:\Users\MIJIMENEZ\Desktop\videoteca\media\static\Montserrat-Bold.ttf",
            uni=True)
    pdf.add_page()

    # Agrega los datos de los préstamos a la página actual
    pdf.generate_table(prestamos_data)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response
# ---------------------------------PDF2-----------------------------------#
# @csrf_exempt    
class GENERATE(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        self.q = q

    def header(self):
        
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('media/images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(480,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(518,1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(458,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(10)

        self.cell(84, 10, 'NOMBRE:', 0, 0, 'L')
       
        x = self.get_x()
        y = self.get_y()

        self.line(x - 65, y + 5, x + 65, y + 5)  
        self.ln(7) 

        self.cell(84, 10, 'Dirección:', 0, 0, 'L')
       
        x = self.get_x()
        y = self.get_y()

        self.line(x - 65, y + 5, x + 65, y + 5)  
        self.ln(7)

        self.cell(84, 10, 'Correo:', 0, 0, 'L')
        
        x = self.get_x()
        y = self.get_y()
        
        self.line(x - 65, y + 5, x + 65, y + 5)  
        self.ln(7)

        self.cell(84, 10, 'Puesto:', 0, 0, 'L')
        
        x = self.get_x()
        y = self.get_y()
        
        self.line(x - 65, y + 5, x + 10, y + 5)  
        self.ln(7)

        self.cell(84, 10, 'Extención:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 10, y + 5)    
        self.ln(27)
   
        self.set_font('Montserrat', 'B', 8)
        self.cell(280, 10, f'Prestamos de folio ({self.q})', 0, 0, 'C')
        self.ln(15)

        self.set_fill_color(31, 237, 237)
        self.set_text_color(255, 255, 255) 
        self.cell(140, 10, 'Código de Barras', 1, 0, '', True)
        self.cell(140, 10, 'Fecha de Devolucón', 1, 0, '', True)
        self.set_text_color(0, 0, 0)
        self.ln()
    
    def footer(self):

        self.ln(10)
        self.set_font('Montserrat', 'B', 8)

        self.cell(84, 10, 'Devuelve:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 10, y + 5)      
        self.ln(7)

        self.cell(84, 10, 'Recibe:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 65, y + 5, x + 10, y + 5)      
        self.ln()

    def generate_Table(self, data):
       
        for row in data:
            self.cell(140, 10, str(row['vide_codigo']), 1)
            self.cell(140, 10, str(row['pres_fecha_devolucion']), 1)
            self.ln()
            
def generar_pdf_modal(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion')

    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="Videoteca.pdf"'  
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = GENERATE('P', 'mm', (300, 350), q)
    pdf.add_font('Montserrat','',
                r"C:\Users\MIJIMENEZ\Desktop\videoteca\media\static\Montserrat-Regular.ttf",
                uni=True)
    pdf.add_font('Montserrat','B',
                r"C:\Users\MIJIMENEZ\Desktop\videoteca\media\static\Montserrat-Bold.ttf",
                uni=True)
    pdf.add_page()
    pdf.generate_Table(queryset)
    
    response.write(pdf.output(dest='S').encode('latin1'))
    return response

# ---------------------------------------------------------------------------------------------------------------------------#

@csrf_exempt      
def json_to_pdf(request,fechaInicio,fechaFin,folio  ):
    dateInicio = datetime.datetime.strptime(fechaInicio, "%d-%m-%Y")
    dateFin = datetime.datetime.strptime(fechaFin, "%d-%m-%Y")
 
    
    input_file = settings.MEDIA_ROOT+ '/Formatos/Compensacion_v1.jrxml'
    CreateJson(dateInicio, dateFin, None, folio)
    output_file = settings.MEDIA_ROOT+ '/Formatos'
    
    json_query = 'contacts.person'

    
    #dictionary = {"contacts": {"person": [ {'Folio':34, 'RFC':61, 'Nombre':82, 'ClaveP':82, 'Categoria':82, 'Codigo':82, 'Compensacion':82, 'CostoHora':82, 'HorasXMes':82, 'Importe':82, 'Fecha':82, 'NoFolio':82}  ] } } 
    #jsonString = json.dumps(dictionary, indent=4)

    #print(jsonString)
    conn = {
      'driver': 'json',
      'data_file': settings.MEDIA_ROOT+ '/Formatos/data.json',
      'json_query': 'compensacion'
   }
    outputFile= settings.MEDIA_ROOT+ '/Formatos/ReporteCompensacion '+fechaInicio+' al '+fechaFin+'.pdf' 
    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
      input_file,
      output_file=outputFile,
      output_formats=["pdf"],
      db_connection=conn
   )
    pyreportjasper.process_report()
    print('Result is the file below.')
   # output_file = output_file + '.pdf'
    if os.path.isfile(outputFile):
    #    print('Report generated successfully!')
        with open(outputFile, 'rb') as pdf:
            response = HttpResponse(pdf.read(),content_type='application/pdf')
            response['Content-Disposition'] = 'filename=ReporteCompensacion '+fechaInicio+' al '+fechaFin+'.pdf'
        return response


def CreateJsonInReport(row, codes, user):
    data = {}
    now = datetime.datetime.now()
    data['reporte']=[]
    data['header'].append({'Nombre': row[0][0] + ' '+ row[0][1]+ ' '+ row[0][2],
                'Direccion':  row[0][5],
                'Puesto':  row[0][6],
                'Extension': row[0][3],
                'Correo':   row[0][4] ,
                'Matricula':   row[0][7],
                'FechaDev': now,
                'Recibe': user,
                'Logo1': settings.MEDIA_ROOT+ '/Formatos/logo-sep.png', 
                'Logo2':  settings.MEDIA_ROOT+ '/Formatos/logo-aprendemx.png' })
                
    with open(settings.MEDIA_ROOT+ '/Formatos/dataHeader.json', 'w',  encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False) 
   
