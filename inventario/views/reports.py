import  json, datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pyreportjasper import PyReportJasper
# from pyreportjasper import JasperGenerator
from fpdf import FPDF
from ..models import Prestamos, DetallePrestamos
from django.http.response import HttpResponse, JsonResponse 
import os
from django.db.models import Q
from reportlab.lib.pagesizes import letter, landscape
from django.db import connections
import json
# from datetime import datetime
from django.db import connections
from datetime import datetime, timedelta, date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
from email.mime.application import MIMEApplication







class PDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        MEDIA_ROOT = settings.MEDIA_ROOT
        self.add_font('Montserrat', '', os.path.join(MEDIA_ROOT, 'static', 'Montserrat-Regular.ttf'), uni=True)
        self.add_font('Montserrat', 'B', os.path.join(MEDIA_ROOT, 'static', 'Montserrat-Bold.ttf'), uni=True)
        self.q = q
        
    def header(self):
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('media/images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(485, 1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440, 1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        # self.ln(3)
        # self.cell(525, 1, 'Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(458, 1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(80)

        if devolucion:
    
            email_institucional  = devolucion['Email']
            extension_telefonica = devolucion['Extension']
            nombre_completo      = devolucion['Obtiene']
            puesto               = devolucion['Puesto']
            
            self.set_xy(10.0, 33.0)
            self.cell(84, 10, 'Nombre:', 0, 0, 'L')
            self.set_xy(27.0, 35.0)
            self.cell(30.0, 6.0, nombre_completo, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Correo:', 0, 0, 'L')
            self.set_xy(27.0, 41.0)
            self.cell(30.0, 6.0, email_institucional, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Puesto:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, puesto, 0, 0, 'L')
            self.ln(3.5)
            self.cell(86, 10, 'Extensión:', 0, 0, 'L')
            self.set_xy(27.0, 53.0)
            self.cell(30.0, 6.0, extension_telefonica, 0, 0, 'L')
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

        self.set_font('Montserrat', 'B', 8)
        self.set_xy(90.5, 50.0)
        self.cell(180, 10, 'Firma:', 0, 0, 'L')     
        x = self.get_x()
        y = self.get_y()
        self.line(x - 167, y + 6, x - 120, y + 6)
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
    detalle_prestamos = DetallePrestamos.objects.filter(Q(pres_folio=q) | Q(vide_codigo=q))
    pres_folios = detalle_prestamos.values_list('pres_folio_id', flat=True)

    prestamos_data = []

    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        if prestamo:
            if detalle_prestamos.filter(pres_folio=pres_folio_id).exists():
                prestamo_data = {
                    "pres_folio": prestamo.pres_folio,
                    "usua_clave": prestamo.usua_clave,
                    "pres_fechahora": prestamo.pres_fechahora,
                    "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                    "pres_estatus": prestamo.pres_estatus,
                    # "usuario_devuelve": detalle_prestamos.filter(pres_folio=pres_folio_id).last().usuario_devuelve,
                    # "usuario_recibe": detalle_prestamos.filter(pres_folio=pres_folio_id).last().usuario_recibe,
                }
                prestamos_data.append(prestamo_data)
                # print(prestamo.usua_clave)
                usuarioRecibio = prestamo.usua_clave
    if usuarioRecibio is not None:
        cursor = connections['users'].cursor()
        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuarioRecibio])

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
                'Matricula'         : usuarioRecibio,
            }

    global devolucion
    devolucion = MatriculaObPrestamo
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = PDF('P', 'mm', (300, 350), q)
    pdf.add_page()
    pdf.generate_table(prestamos_data)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response

# ---------------------------------PDF2-----------------------------------#
# @csrf_exempt    
class GENERATE(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        MEDIA_ROOT = settings.MEDIA_ROOT
        # print('Este entra a inventario',MEDIA_ROOT)
        self.add_font('Montserrat', '',  os.path.join(MEDIA_ROOT, 'static','Montserrat-Regular.ttf'), uni=True)
        self.add_font('Montserrat', 'B', os.path.join(MEDIA_ROOT, 'static','Montserrat-Bold.ttf'), uni=True)

        self.q = q

    def header(self):
        
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('media/images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(485,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(440,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        # self.cell(525,1, 'Audiovisual', 0, 20, 'C')
        # self.ln(3)
        self.cell(458,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(80)

        if devolucion:
        
            email_institucional  = devolucion['Email']
            extension_telefonica = devolucion['Extension']
            nombre_completo      = devolucion['Devuelve']
            puesto               = devolucion['Puesto']
           
            self.set_xy(10.0, 33.0)
            self.cell(84, 10, 'Nombre:', 0, 0, 'L')
            self.set_xy(27.0, 35.0)
            self.cell(30.0, 6.0, nombre_completo, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Correo:', 0, 0, 'L')
            self.set_xy(27.0, 41.0)
            self.cell(30.0, 6.0, email_institucional, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Puesto:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, puesto, 0, 0, 'L')
            self.ln(3.5)
            self.cell(86, 10, 'Extensión:', 0, 0, 'L')
            self.set_xy(27.0, 53.0)
            self.cell(30.0, 5.0, extension_telefonica, 0, 0, 'L')
            self.ln(15)         
            self.set_font('Montserrat', 'B', 8)
            self.cell(280, 10, f'Préstamos con folio ({self.q})', 0, 0, 'C')
            self.ln(15)

            self.set_fill_color(144, 12, 63)
            self.set_text_color(255, 255, 255) 
            self.cell(60, 10, 'Código de Barras', 1, 0, '', True)
            self.cell(60, 10, 'Usuario Devuelve', 1, 0, '', True)
            self.cell(60, 10, 'Fecha de Devolucón', 1, 0, '', True)
            self.cell(60, 10, 'Usuario Recibe', 1, 0, '', True)
            self.cell(25, 10, 'Estatus', 1, 0, '', True)
            self.set_text_color(0, 0, 0)
            self.ln(10)
    
    def footer(self):
        self.set_font('Montserrat', 'B', 8)

        if userRecibe:
          
            name  = userRecibe['Recibe']        
            self.set_xy(90.0, 33.0)
            self.cell(180, 10, 'Recibe:', 0, 0, 'L')
            self.set_xy(108.0, 35.0)
            self.cell(30.0, 6.0, name, 0, 0, 'L')

        if devolucion:
           
            name  = devolucion['Devuelve']          
            self.set_xy(90.0, 39.0)
            self.cell(180, 10, 'Devuelve:', 0, 0, 'L')
            self.set_xy(108.0, 41.0)
            self.cell(30.0, 6.0, name, 0, 0, 'L')
            self.set_xy(90.5, 50.0)
            self.cell(180, 10, 'Firma:', 0, 0, 'L')
            x = self.get_x()
            y = self.get_y()
            self.line(x - 167, y + 6, x - 120, y + 6)
            self.set_y(-15)
            self.set_font('Montserrat', '', 8)
            self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_Table(self, data):
        total_registros = len(data)
        for row in data:
            self.cell(60, 10, str(row['vide_codigo_id']), 1)
              # Comprueba si pres_fecha_devolucion no es None 
            if row['pres_fecha_devolucion']:
                fecha_devolucion = row['pres_fecha_devolucion'].strftime('%d-%m-%Y')
            else:
                fecha_devolucion = "Sin Devolver"  # Maneja el caso en que sea None
            
            self.cell(60, 10, str(row['usuario_devuelve']), 1)
            self.cell(60, 10, fecha_devolucion, 1)
            self.cell(60, 10, str(row['usuario_recibe']), 1)
            
            if row['depr_estatus'] == 'I':
                self.cell(25, 10, "Entregado", 1)
            else:
                self.cell(25, 10, "En préstamo", 1)

            self.ln()
        self.cell(0, 10, f'Total de registros: {total_registros}', 0, 0, 'C')
        self.ln(10)

            

def generar_pdf_modal(request):

    q = int(request.GET.get("q"))
    queryset = DetallePrestamos.objects.filter(pres_folio=q).values('vide_codigo_id', 'pres_fecha_devolucion', 'usuario_devuelve', 'usuario_recibe','depr_estatus')
    detalle_prestamos = queryset.last() if queryset else None 

    nombres = ''
    apellido1 = ''
    apellido2 = ''
    puesto = ''
    email_institucional = ''
    extension_telefonica = ''

    if detalle_prestamos:
        usuario_devuelve = detalle_prestamos['usuario_devuelve']
        usuario_recibe = detalle_prestamos['usuario_recibe']
        # print(usuario_recibe)
        # 
        # detalle_matricula = DetallePrestamos.objects.filter(usuario_devuelve=usuario_devuelve).first()
        detalle_matricula = DetallePrestamos.objects.filter( usuario_devuelve=usuario_devuelve, usuario_recibe=usuario_recibe ).first()
        muestraData = []

        if detalle_matricula is not None:
            matricula_data = {
                "UsuarioDevuelve": detalle_matricula.usuario_devuelve,
                "UsuarioRecibe": detalle_matricula.usuario_recibe
            }
            muestraData.append(matricula_data)
            if muestraData:
                usuario_devuelve = muestraData[0]["UsuarioDevuelve"]
                usuario_recibe = muestraData[0]["UsuarioRecibe"]

        cursor = connections['users'].cursor()
        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_devuelve] )
        row = cursor.fetchone() 

        if row is not None:
            nombres = row[0]
            apellido1 = row[1]
            apellido2 = row[2]
            puesto = row[3] 
            email_institucional = row[4]
            extension_telefonica = row[5]

        nombre_completo = f"{nombres} {apellido1} {apellido2}"  

        MatriculaDevuelve = {
            'Devuelve': nombre_completo,
            'Puesto': puesto,
            'Email': email_institucional,
            'Extension': extension_telefonica, 
            'Matricula': usuario_devuelve,
        }

        cursor.execute("select nombres, apellido1, apellido2, puesto, email_institucional, extension_telefonica from people_person where matricula = %s", [usuario_recibe])
        row = cursor.fetchone()

        if row is not None:
            nombres = row[0]
            apellido1 = row[1]
            apellido2 = row[2]
            puesto = row[3]
            email_institucional = row[4]
            extension_telefonica = row[5]

        nombre_completo2 = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
        MatriculaRecibe = {
            'Recibe': nombre_completo2,
            'Puesto': puesto,
            'Email': email_institucional,
            'Extension': extension_telefonica, 
            'Matricula': usuario_recibe,
        }

        # devolucion = MatriculaDevuelve
        # userRecibe = MatriculaRecibe

        global userRecibe, devolucion 
        userRecibe = MatriculaRecibe
        devolucion = MatriculaDevuelve
            

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Videoteca_Código_{q}.pdf"'
    pdf = GENERATE('P', 'mm', (300, 350), q)
    pdf.add_page()
    pdf.generate_Table(queryset)
    response.write(pdf.output(dest='S').encode('latin1'))
    return response

# ---------------------------------------------------------------------------------------------------------------------------#
class PDF_FOLIO(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4', q=None):
        super().__init__(orientation, unit, format)
        MEDIA_ROOT = settings.MEDIA_ROOT
        self.add_font('Montserrat', '',  os.path.join(MEDIA_ROOT, 'static','Montserrat-Regular.ttf'), uni=True)
        self.add_font('Montserrat', 'B', os.path.join(MEDIA_ROOT, 'static','Montserrat-Bold.ttf'), uni=True)
        self.q = q
        
    def header(self):
        self.image('media/images/EducaciónAprende.jpeg', x=10, y=8, w=50)
        self.image('media/images/logo-aprendemx.png', x=65, y=5, w=50)
        self.ln()

        self.set_font('Montserrat', 'B', 8)
        self.cell(400,1, 'SECRETARÍA DE EDUCACIÓN PÚBLICA', 0, 10, 'C')
        self.ln(3)
        self.cell(355,1, 'Subdirección de Sistematización de Acervos y Desarrollo Audiovisual', 0, 20, 'C')
        self.ln(3)
        self.cell(372,1, 'Departamento de Conservación de Acervos Videográficos', 0, 20, 'C')
        self.ln(80)

        if userobjPrestamo:
            email_institucional  = userobjPrestamo['Email']
            extension_telefonica = userobjPrestamo['Extension']
            nombre_completo      = userobjPrestamo['Obtiene']
            puesto               = userobjPrestamo['Puesto']
           
            self.set_xy(10.0, 33.0)
            self.cell(84, 10, 'Nombre:', 0, 0, 'L')
            self.set_xy(27.0, 35.0)
            self.cell(30.0, 6.0, nombre_completo, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Correo:', 0, 0, 'L')
            self.set_xy(27.0, 41.0)
            self.cell(30.0, 6.0, email_institucional, 0, 0, 'L')
            self.ln(3.5)
            self.cell(84, 10, 'Puesto:', 0, 0, 'L')
            self.set_xy(27.0, 47.0)
            self.cell(30.0, 6.0, puesto, 0, 0, 'L')
            self.ln(3.5)
            self.cell(86, 10, 'Extensión:', 0, 0, 'L')
            self.set_xy(27.0, 53.0)
            self.cell(30.0, 6.0, extension_telefonica, 0, 0, 'L')
            self.ln(15)         
            self.set_font('Montserrat', 'B', 8)
            self.cell(224, 10, f'Prestamos de la cinta ({self.q})', 0, 0, 'C')
            self.ln(15)
            
            

            self.set_fill_color(144, 12, 63)
            self.set_text_color(255, 255, 255) 
            self.cell(30, 10, 'Consecutivo', 1, 0, '', True)
            self.cell(40, 10, 'Folio', 1, 0, '', True)
            self.cell(40, 10, 'Usuario', 1, 0, '', True)
            self.cell(40, 10, 'Fecha prestamo', 1, 0, '', True)
            self.cell(30, 10, 'Estatus', 1, 0, '', True)
            self.cell(40, 10, 'Código barras', 1, 0, '', True)
            self.set_text_color(0, 0, 0)
            self.ln()
            
    def footer(self):
        self.set_font('Montserrat', 'B', 8)
        self.set_xy(90.5, 50.0)
        self.cell(180, 10, 'Firma:', 0, 0, 'L')
        x = self.get_x()
        y = self.get_y()
        self.line(x - 167, y + 6, x - 120, y + 6)
        self.set_y(-15)
        self.set_font('Montserrat', '', 8)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def generate_table(self, data):
        consecutivo = 1
        total_registros = len(data)  
        for row in data:
            self.cell(30, 10, str(consecutivo), 1)  # Agregar consecutivo
            consecutivo += 1 
            self.cell(40, 10, str(row['pres_folio']), 1)
            self.cell(40, 10, str(row['usua_clave']), 1)
            if row['pres_fechahora']:
                formatted_date = row['pres_fechahora'].strftime('%d-%m-%Y')
                self.cell(40, 10, formatted_date, 1)
            else:
                self.cell(40, 10, '', 1)  # Celda vacía si no hay fecha
            if row['pres_estatus'] == 'I':
                self.cell(30, 10, "Entregado", 1)
            else:
                self.cell(30, 10, "En préstamo", 1)
            self.cell(40, 10, str(row['codigo_barras']), 1)
            self.ln()  # Salto de línea para pasar a la siguiente fila

        self.cell(0, 10, f'Total de registros: {total_registros}', 0, 0, 'C')
        self.ln(15)  # Salto de línea adicional


def generate_pdf_resgister_folio(request):
    q = request.GET.get('q')
    detalle_prestamos = DetallePrestamos.objects.filter(pres_folio=q)
    pres_folios = detalle_prestamos.values_list('pres_folio_id', flat=True)

    prestamos_data = []

    for pres_folio_id in pres_folios:
        prestamo = Prestamos.objects.filter(pres_folio=pres_folio_id).first()
        detalles_prestamo = DetallePrestamos.objects.filter(pres_folio=pres_folio_id)

        if prestamo and detalles_prestamo.exists():
            matri = prestamo.usua_clave

            for detalle in detalles_prestamo:
                maestro_cintas = detalle.vide_codigo
                codigo_barras = maestro_cintas.video_cbarras if maestro_cintas else None

                if not any(entry["codigo_barras"] == codigo_barras for entry in prestamos_data):
                    prestamo_data = {
                        "pres_folio": prestamo.pres_folio,
                        "usua_clave": prestamo.usua_clave,
                        "pres_fechahora": prestamo.pres_fechahora,
                        "pres_fecha_devolucion": prestamo.pres_fecha_devolucion,
                        "pres_estatus": prestamo.pres_estatus,
                        "codigo_barras": codigo_barras,
                    }
                    prestamos_data.append(prestamo_data)

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
            }

        global userobjPrestamo
        userobjPrestamo = MatriculaObPrestamo

        # Generar el PDF y almacenarlo en un BytesIO
        pdf_bytes = BytesIO()
        pdf = PDF_FOLIO('P', 'mm', (240, 250), q)
        pdf.add_page()
        pdf.generate_table(prestamos_data)
        pdf_bytes.write(pdf.output(dest='S').encode('latin1'))

        # Configurar el correo electrónico
        from_email = '333.mija@gmail.com'
        password = 'roxbrhvwyjxdyxvg'
        to_email = email_institucional

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = 'Asunto del correo'

        body = 'Este es el cuerpo del correo electrónico.'
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo PDF al correo electrónico desde BytesIO
        pdf_bytes.seek(0)  # Reiniciar el cursor al principio del BytesIO
        part = MIMEApplication(pdf_bytes.read(), _subtype='pdf')
        pdf_bytes.seek(0)  # Reiniciar el cursor nuevamente al principio del BytesIO
        part.add_header('Content-Disposition', f'attachment; filename="Videoteca_Código_{q}.pdf"')
        msg.attach(part)

        # Enviar el correo electrónico
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        print("Correo electrónico enviado correctamente a:", to_email)

        return HttpResponse(content=pdf_bytes.getvalue(), content_type='application/pdf')

    return HttpResponse("No se encontró la matrícula correspondiente.")

@csrf_exempt      
def json_to_pdf(request, row, codes, user):
    # RESOURCES_DIR = settings.MEDIA_ROOT + '/Formatos/montserrat.jar'
    input_file = settings.MEDIA_ROOT + '/Formatos/ReporteDevolucion.jrxml'
    CreateJsonInReport(row, codes, user)
    output_file = settings.MEDIA_ROOT + '/Formatos/ReporteDevolucion.pdf'  # Specific file path
    conn = {
        'driver': 'json',
        'data_file': settings.MEDIA_ROOT + '/Formatos/dataHeader.json',
        'json_query': 'reporte'
    }
    pyreportjasper = PyReportJasper()
    pyreportjasper.config(
        input_file,
        output_file=output_file,
        output_formats=["pdf"],
        db_connection=conn,
        # resource=RESOURCES_DIR
    )
    pyreportjasper.process_report()
    return output_file  # Return the file path
   
  
def GetFilePdf(request):
    file = request.GET.get('q')
    if os.path.isfile(file):
        print('Report generated successfully!')
        with open(file, 'rb') as pdf:
            response = HttpResponse(pdf.read(),content_type='application/pdf')
            response['Content-Disposition'] = 'filename=ReporteDevolucion.pdf'
        return response
  
    else:
        print('Report not generated!')
  
def CreateJsonInReport(row, codes, user):
    data = {}
    i = 0
    now = datetime.now()
    data['reporte'] = []
    codeJson = json.loads(codes)

    for code in enumerate(codeJson):
        if code[1] is not None:
            i += 1
            data['reporte'].append({
                'Nombre': row[0][0] + ' ' + row[0][1] + ' ' + row[0][2],
                'Direccion': row[0][5],
                'Puesto': row[0][6],
                'Extension': row[0][3],
                'Correo': row[0][4],
                'Matricula': row[0][7],
                'FechaDev': now.strftime("%d-%m-%Y"),
                'Recibe': user,
                'Logo1': settings.MEDIA_ROOT + '/Formatos/logo-sep.png',
                'Logo2': settings.MEDIA_ROOT + '/Formatos/logo-aprendemx.png',
                'Codigo': code[1],
                'Consecutivo': i
            })

    total_registros = len(data['reporte']) 
    print('Total de registros en data:', total_registros)
    
    for item in data['reporte']:
        item['total'] = total_registros  # Agrega el total de registros a cada objeto

    with open(settings.MEDIA_ROOT + '/Formatos/dataHeader.json', 'w', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)



#-------------------------------------------------------------------------------------------------#

def getReport(request):
    search_type = request.GET.get('searchType')
    day = request.GET.get('day')
    week = request.GET.get('week')
    month = request.GET.get('month')
    matricula = request.GET.get('matricula')
    
    # print('Busque', matricula)
    
    # Seleccionar el tipo de búsqueda
    if search_type == 'byDay':
        day_datetime = datetime.strptime(day, "%Y-%m-%d")
        prestamos = Prestamos.objects.filter(pres_fecha_prestamo__date=day_datetime)
        return generateJson(prestamos, matricula, day=day, search_type=search_type)
      
    elif search_type == 'byWeek':
        year, week_number = map(int, week.split('-W'))
        inicio_semana = datetime.strptime(f"{year}-W{week_number}-1", "%Y-W%W-%w").date()
        fin_semana = inicio_semana + timedelta(days=6)
        queryset = Prestamos.objects.filter(pres_fecha_prestamo__range=(inicio_semana, fin_semana)).order_by('-pres_fecha_prestamo')
        return generateJson(queryset, matricula, week=week, search_type=search_type)
       
    elif search_type == 'byMonth':
        year, month_number = map(int, month.split('-'))
        queryset = Prestamos.objects.filter(pres_fecha_prestamo__year=year, pres_fecha_prestamo__month=month_number).order_by('-pres_fecha_prestamo')
        year, month_number = map(int, month.split('-'))
        queryset = Prestamos.objects.filter(pres_fecha_prestamo__year=year, pres_fecha_prestamo__month=month_number).order_by('-pres_fecha_prestamo')
        return generateJson(queryset, matricula, month=month, search_type=search_type)
       
    elif matricula and request.GET.get('checkAdeudos'):
        prestamos = Prestamos.objects.filter(usua_clave=matricula, pres_estatus='X')
        return generateJson(prestamos, matricula, search_type='matricula')
    
    else:
        return HttpResponse("Tipo de búsqueda no válido.")
    

def generateJson(queryset, matricula=None, day=None, week=None, month=None, search_type=None):
    # Diccionario para mapear los tipos de reporte de inglés a español
    tipos_reporte_espanol = {
        'byDay': 'POR DÍA',
        'byWeek': 'SEMANAL',
        'byMonth': 'MENSUAL',
        'matricula': 'POR ADEUDO'
    }

    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mesesEnEspaniol = ['Enero', 'Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembe', 'Octube','Noviembre','Diciembre' ]
    
    prestamos_list = list(queryset.values())
    total_registros = len(prestamos_list)
    for i, prestamo in enumerate(prestamos_list, start=1):
        prestamo['consecutivo'] = i
    matriculas_list = [prestamo['usua_clave'] for prestamo in prestamos_list]
    cursor = connections['users'].cursor()
    
    if matriculas_list:
        cursor.execute("SELECT matricula, nombres, apellido1, apellido2 FROM people_person WHERE matricula IN %s", (tuple(matriculas_list),))
        users_data = cursor.fetchall()
    else:
        users_data = []

    usuarios_dict = {row[0]: f"{row[1]} {row[2]} {row[3]}" if row[3] else f"{row[1]} {row[2]}" for row in users_data}        

    for prestamo in prestamos_list:
        matricula = prestamo['usua_clave']
        nombre_usuario = usuarios_dict.get(matricula, '')
        prestamo['nombre_usuario'] = nombre_usuario
        prestamo['aprende'] =  os.path.join(settings.MEDIA_ROOT, 'Formatos', 'logo-aprendemx.png')
        prestamo['sep'] =  os.path.join(settings.MEDIA_ROOT, 'Formatos', 'EducaciónAprende.jpeg')
        prestamo['tipo_reporte'] = tipos_reporte_espanol.get(search_type, search_type)
        prestamo['total_registros'] = total_registros
        prestamo['fecha_hora_actual'] = fecha_hora_actual

        if search_type == 'byDay':
            fecha_dt = datetime.strptime(day, "%Y-%m-%d")
            fecha = f"Reporte del día {fecha_dt.day} de {mesesEnEspaniol[fecha_dt.month - 1]} de {fecha_dt.year}"
        elif search_type == 'byWeek':
            year, week_number = map(int, week.split('-W'))
            inicio_semana = datetime.strptime(f"{year}-W{week_number}-1", "%Y-W%W-%w").date()
            fin_semana = inicio_semana + timedelta(days=4)
            fecha = f"Reporte del  {inicio_semana.day} de {mesesEnEspaniol[inicio_semana.month - 1]} al {fin_semana.day} de {mesesEnEspaniol[fin_semana.month - 1]} de {year}"
        elif search_type == 'byMonth':
            year, month_number = map(int, month.split('-'))
            fecha = f"Reporte del mes de {mesesEnEspaniol[month_number - 1]} de {year}"
        else:
            fecha = ""
        prestamo['fecha']=fecha

    # Convertir objetos datetime a cadenas de texto antes de serializar
    for prestamo in prestamos_list:
        prestamo['pres_fecha_prestamo'] = prestamo['pres_fecha_prestamo'].strftime('%Y-%m-%d %H:%M:%S')

    if prestamos_list:
        # Crear un diccionario con la lista de préstamos
        data = {'prestamos': prestamos_list}

        json_file_path = os.path.join(settings.MEDIA_ROOT, 'Formatos', 'reportePrestamo.json')

        # Escribir los datos en el archivo JSON
        with open(json_file_path, 'w', encoding='utf8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False, default=str)

        input_file = os.path.join(settings.MEDIA_ROOT, 'Formatos', 'ReportePorDía.jrxml')
        output_file = os.path.join(settings.MEDIA_ROOT, 'Formatos', 'ReportePorDía.pdf')
        conn = {
            'driver': 'json',
            'data_file': os.path.join(settings.MEDIA_ROOT, 'Formatos', 'reportePrestamo.json'),
            'json_query': 'prestamos'
        }

        pyreportjasper = PyReportJasper()
        pyreportjasper.config(
            input_file,
            output_file=output_file,
            output_formats=["pdf"],
            db_connection=conn,
        )
        pyreportjasper.process_report()

        print("Archivo JSON creado exitosamente en:", json_file_path)

        # Descargar el archivo PDF generado
        file_path = os.path.join(settings.MEDIA_ROOT, 'Formatos', 'ReportePorDía.pdf')
        if os.path.isfile(file_path):
            print('Reporte generado exitosamente!')
            with open(file_path, 'rb') as pdf:
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=ReportePorDía.pdf'
            return response
        else:
            print('¡Error! El reporte no se generó correctamente.')
            return HttpResponse("¡Error! El reporte no se generó correctamente.")
    else:
        print("No se encontraron préstamos para esta búsqueda.")
        return HttpResponse("No se encontraron préstamos para esta búsqueda.")
