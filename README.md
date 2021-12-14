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