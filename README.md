```
python manage.py startapp inventario

python manage.py makemigrations inventario
python manage.py migrate
python manage.py migrate inventario 0001

python manage.py createsuperuser
```

## Database
```
SET client_encoding = 'LATIN1';

CREATE DATABASE pepe WITH TEMPLATE = template0 OWNER = postgres LC_COLLATE = 'es_ES.iso88591' LC_CTYPE = 'es_ES.iso88591';
```

## Virtual env
```
pip install virtualenv
virtualenv env
source env/bin/activate
pip install django
pip install psycopg2-binary

python manage.py makemigrations
python manage.py migrate
```
### Windows
```
venv\Scripts\activate
```


## Create User
```
python manage.py createsuperuser
```

## Migrate data
```
python manage.py loaddata
```


# Resources

[guía de estilo para gob.mx](https://www.gob.mx/guias/grafica/)


Usuario: asdfasdfasdf
Inventario
Prestamo de material videograbado
Calificación de material videograbado
Ingreso de material a videoteca
Consulta
Reportes
Logout

Búsqueda:
    - Código de barras
    - Formato de cinta
    - Número de cinta
    - Tipo de cinta
    - Año inventario

Datos generales:
    Videoteca
    Estatus de la cinta
    Fecha de califiación
    Fecha ingreso
    Año de producción
    Inventario
    Productor
    Coordinador
    Última actualización
    Observaciones
    Tipo de serie:
    Origen de Serie
    Target

Programas grabados en la cinta actual
    Folio | código
    Duración
    TX
    Título de la serie
    Título del programa
    Subtítulo de la serie
    Subtítulo del programa

Cintas relacionadas
    - Código
    - Tio
    - Formato
    -- Consultar insertar aceptar cancelar borrar
Programas contenidos en las cintas relacionadas
    - Serie
    - Programa
    - Subtítulo
    -- Consultar insertar aceptar cancelar borrar60
