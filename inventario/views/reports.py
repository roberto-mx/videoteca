import textwrap, operator, base64, json, datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pyreportjasper import PyReportJasper
from django.core import serializers
from fpdf import FPDF
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from ..models import Prestamos, DetallePrestamos, MaestroCintas, DetalleProgramas, Videos
from django.http.response import HttpResponse, JsonResponse
import os 
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
        #self.drawline    
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
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = PDF('P', 'mm', (300, 350), q)
    # Abre una nueva página en el documento PDF
    pdf.add_page()

    # Agrega los datos de los préstamos a la página actual
    pdf.generate_table(prestamos_data)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response
# ---------------------------------PDF2----------------------------------------------------------------------------------------
# @csrf_exempt    
class GENERATE(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        self.q = q

    def header(self):
        
        # Configuración de la cabecera del PDF
        self.image('images/EducaciónAprende.jpeg', x=10, y=8, w=35)
        self.image('images/logo-aprendemx.png', x=46, y=7, w=35)
        self.ln()

        self.set_font('Arial', 'B', 6)
        self.cell(323,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(293,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(351.5,1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(306.5,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(40)

        self.set_font('Arial', 'B', 8)
        self.cell(84, 10,   'NOMBRE:      _______________________________', 0, 0, 'C')
        # self.ln(7)
        self.cell(103, 10,  'DIRECCIÓN:   _______________________________', 0, 0, 'C')
        self.ln(17)
        self.cell(83, 10,   'PUESTO:      _______________________________', 0, 0, 'C')

        self.cell(103, 10,  'EXTENSIÓN:   _______________________________', 0, 0, 'C')
        # self.cell(103, 10,  'CORREO:      _______________________________', 0, 0, 'C')
        self.ln(40)
        
        self.set_font('Arial', 'B', 15)
        self.cell(180, 10, f'Folio de la cinta ({self.q})', 0, 0, 'C')
        self.ln(20)
        
    def footer(self):

        self.ln(40)
        self.set_font('Arial', 'B', 8)
        self.cell(83, 10, 'RECIBE: _______________________________', 0, 0, 'C')
        self.cell(93, 10, 'DEVUELVE: _______________________________', 0, 0, 'C')
        self.ln()

        # self.cell(103, 10, '_______________________________', 0, 0, 'C')
        # self.ln(8)
        # self.cell(200, 10, '_______________________________', 0, 0, 'C')
        # self.ln()

        # Configuración del pie de página del PDF
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_Table(self, data):
        # Generación del contenido de la tabla en el PDF
        self.set_fill_color(31, 237, 237)
        self.set_text_color(6, 28, 28) # Establece el color de la letra en blanco
        self.cell(90, 10, 'Código de Barras', 1, 0, '', True)
        self.cell(90, 10, 'Fecha de Devolucón', 1, 0, '', True)
        self.set_text_color(0, 0, 0)
        self.ln()

        for row in data:
            self.cell(90, 10, str(row['vide_codigo']), 1)
            self.cell(90, 10, str(row['pres_fecha_devolucion']), 1)
            self.ln()

def generar_pdf_modal(request):
    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo', 'pres_fecha_devolucion')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Folio_{q}.pdf"'
    pdf = GENERATE('P', 'mm', (200, 380), q)
    pdf.add_page()
    pdf.generate_Table(queryset)
    
    response.write(pdf.output(dest='S').encode('latin1'))
    return response
   


# ---------------------------------------------------------------------------------------------------------------------------#
def xml_to_pdf():
   RESOURCES_DIR = os.path.abspath(settings.MEDIA_ROOT)
   REPORTS_DIR = os.path.abspath(os.path.dirname(__file__))
   input_file = settings.MEDIA_ROOT+ '/reports/main.jrxml'
   output_file = settings.MEDIA_ROOT+ '/reports/report'
   data_file = settings.MEDIA_ROOT+ '/reports/contacts.xml'
   pyreportjasper = PyReportJasper()
   pyreportjasper.config(
      input_file,
      output_file,
      output_formats=["pdf"],
      db_connection={
          'driver': 'xml',
          'data_file': data_file,
          'xml_xpath': '/',
      }, 
      resource="C:/Users/Cmalvaez/Documents/"
   )
   pyreportjasper.process_report()
   print('Result is the file below.')
   print(output_file + '.pdf')




@csrf_exempt      
def json_to_pdf(request, row, codes, user ):
    RESOURCES_DIR = settings.MEDIA_ROOT+ '/Formatos/montserrat.jar'
    input_file = settings.MEDIA_ROOT+ '/Formatos/ReporteDevolucion.jrxml'
    CreateJsonInReport(row, codes, user)
    output_file = settings.MEDIA_ROOT+ '/Formatos'
    conn = {
      'driver': 'json',
      'data_file': settings.MEDIA_ROOT+ '/Formatos/dataHeader.json',
      'json_query': 'reporte'
   }
    outputFile= settings.MEDIA_ROOT+ '/Formatos/ReporteDevolucion.pdf' 
    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
      input_file,
      output_file=outputFile,
      output_formats=["pdf"],
      db_connection=conn,
      resource=RESOURCES_DIR
   )
    pyreportjasper.process_report()
    print('Result is the file below.')
     # output_file = output_file + '.pdf'
    if os.path.isfile(outputFile):
    #    print('Report generated successfully!')
        with open(outputFile, 'rb') as pdf:
            response = HttpResponse(pdf.read(),content_type='application/pdf')
            response['Content-Disposition'] = 'filename=ReporteDevolucion.pdf'
        return response
  

def CreateJsonInReport(row, codes, user):
    data = {}
    i = 0
    now = datetime.datetime.now()
    data['reporte']=[]
    codeJson = json.loads(codes)
    for code in enumerate(codeJson):
        if code[1] != None :
            i+=1
            data['reporte'].append({'Nombre': row[0][0] + ' '+ row[0][1]+ ' '+ row[0][2],
                'Direccion':  row[0][5],
                'Puesto':  row[0][6],
                'Extension': row[0][3],
                'Correo':   row[0][4] ,
                'Matricula':   row[0][7],
                'FechaDev': now.strftime("%d-%m-%Y"),
                'Recibe': user,
                'Logo1': settings.MEDIA_ROOT+ '/Formatos/logo-sep.png', 
                'Logo2':  settings.MEDIA_ROOT+ '/Formatos/logo-aprendemx.png', 
                'Codigo': code[1], 
                'Consecutivo': i })
                
    with open(settings.MEDIA_ROOT+ '/Formatos/dataHeader.json', 'w',  encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False) 
   
