# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia los archivos de requerimientos al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install -r requirements.txt

# Copia el contenido de la aplicación al contenedor
COPY . .

# Puerto en el que se ejecutará la aplicación
EXPOSE 8086

# Comando para ejecutar la aplicación (ajusta según tu proyecto)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8086"]
