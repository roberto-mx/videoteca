FROM python:3.9

# Establece el directorio de trabajo en el contenedor
# WORKDIR /opt/videoteca

WORKDIR /app

# Copia el archivo de requisitos al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install -r requirements.txt

# Copia el contenido de tu proyecto (incluyendo manage.py) al contenedor
COPY . .

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8085

# Comando para iniciar la aplicación Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8085"]
