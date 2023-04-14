import textwrap, operator, base64, json, datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from pyreportjasper import PyReportJasper

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



def CreateJson(dateInicio, dateFin, condicion, folio):
    data = {}
    horas = 0
    total = 0
    data['compensacion']=[]
    if condicion == None:
        compensaciones = Compensaciones.objects.all().order_by('info_person__rfc')
    else:
        compensaciones = Compensaciones.objects.all().filter(Q(info_person__cat_area_org__pk = condicion))
    if compensaciones.count() > 0:
        j=0
        for i, compen in enumerate(compensaciones):
            print(compen.info_person.apellido1 +" "+ compen.info_person.apellido2 +" "+ compen.info_person.nombres)
            horas = calculoIncidenciasPersona(dateInicio, dateFin, compen.info_person)
            horas = math.floor(horas)
            if horas <= 90:
                importe = Decimal(horas) * (compen.compensacion.montoUnitario / 90)
            elif horas == 0:
                importe = 0
            else:
                horas = 90
                importe = compen.compensacion.montoUnitario 
            total += importe
            if horas != 0:
                data['compensacion'].append({'Folio': j+1,
                'NoFolio': folio+j,
                'Area': compen.info_person.cat_area_org.nombre,
                'RFC': compen.info_person.rfc,
                'Nombre':  compen.info_person.apellido1.upper() +" "+ compen.info_person.apellido2.upper() +" "+ compen.info_person.nombres.upper() ,
                'ClaveP':  compen.info_person.clave_presupuestal,
                'Categoria': compen.compensacion.nombre,
                'Codigo': compen.compensacion.codigo,
                'Compensacion': '$ '+ str(compen.compensacion.montoUnitario),
                'CostoHora': str(round(compen.compensacion.montoUnitario / 90, 4) ),
                'HorasXMes': str(horas),
                'Importe': '$ ' +str("{:,}".format(round(importe, 2))),
                'Fecha': str(dateInicio.strftime("%d-%m-%Y")) + ' al ' +str(dateFin.strftime("%d-%m-%Y")), 
                'Total': '$ ' + str("{:,}".format(round( total, 2))), 
                'Logo1': settings.MEDIA_ROOT+ '/Formatos/logo-sep.png', 
                'Logo2':  settings.MEDIA_ROOT+ '/Formatos/logo-aprendemx.png' })
                j+=1
        with open(settings.MEDIA_ROOT+ '/Formatos/data.json', 'w',  encoding='utf8') as file:
            json.dump(data, file, ensure_ascii=False) 
    return compensaciones.count()