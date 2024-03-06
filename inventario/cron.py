import django
import os
from datetime import timedelta
from django.utils import timezone
from django_cron import CronJobBase, Schedule
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from email.mime.application import MIMEApplication
from urllib.parse import quote
from collections import defaultdict
from django.db import connections



# Configurar las configuraciones de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videoteca.settings')
django.setup()

from inventario.models import Prestamos


def my_cron_job(): 
    prestamos_por_usuario = defaultdict(list)

    # Agrupar préstamos pendientes por usuario
    prestamos = Prestamos.objects.filter(
        pres_fecha_prestamo__lte=timezone.now() - timedelta(days=7),
        pres_estatus='X',
    )

    for prestamo in prestamos:
        prestamos_por_usuario[prestamo.usua_clave].append(prestamo)

    # Iterar sobre los préstamos por usuario y enviar un correo electrónico a cada uno
    for matricula, prestamos_usuario in prestamos_por_usuario.items():
        # Obtener información del usuario (puedes personalizar esto según tu modelo de datos)
        cursor = connections['users'].cursor()
        cursor.execute("SELECT nombres, apellido1, apellido2, email_institucional FROM people_person WHERE matricula = %s", [matricula])
        row = cursor.fetchone()
        if row is not None:
            nombres, apellido1, apellido2, email_institucional = row
            nombre_completo = f"{nombres} {apellido1} {apellido2}" if apellido2 else f"{nombres} {apellido1}"
            to_email = email_institucional

            from_email = "videoteca.aprende@nube.sep.gob.mx"
            password = "lK91M9l/V6#i"
            smtp_server = "smtp.office365.com"
            smtp_port = "587"

            message = MIMEMultipart()
            message['From'] = from_email
            message['To'] = to_email
            message['Subject'] = '¡Urgente!'
            
            # Construir el cuerpo del correo electrónico
            body = f'''
            Se te envía este correo como recordatorio de que no has hecho la devolución de préstamos, con los siguientes folios<br><br>
            '''

            for prestamo in prestamos_usuario:
                fecha_prestamo = prestamo.pres_fecha_prestamo.date()
                fecha_actual = fecha_prestamo
                dias_habiles_encontrados = 0
                desplazamiento = timedelta(days=1)

                while dias_habiles_encontrados < 7:
                    # Calcular la fecha de vencimiento sumando 1 día a la vez
                    fecha_actual += desplazamiento
                    
                    # Verificar si la fecha actual es un día hábil (de lunes a viernes)
                    if fecha_actual.weekday() < 5:
                        dias_habiles_encontrados += 1

                fecha_vencimiento = fecha_actual.strftime('%Y-%m-%d')
                
                body += f"Folio: <b>{prestamo.pres_folio}</b> Fecha que venció: <b>{fecha_vencimiento}</b><br>"

            body += f"<br>Se te hace la invitación a devolver dichas cintas, ya que de lo contrario no podrás solicitar más préstamos.<br><br>Se agradece tu atención <b>{nombre_completo}</b>.<br><br>"
            body += f"<b>ATT. Videoteca Aprende.mx</b>"

            # Adjunta el cuerpo del correo al mensaje
            message.attach(MIMEText(body, 'html'))

            # Envía el correo electrónico al usuario
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, password)
            text = message.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()