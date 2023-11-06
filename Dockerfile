FROM adoptopenjdk:11-jre-hotspot

# Instala Python 3.9
RUN apt-get update && apt-get install -y python3.9

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos y scripts necesarios
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install -r requirements.txt

# Copia el resto de tu aplicación
COPY . .

# Exponer el puerto si es necesario
EXPOSE 8085

# Comando para iniciar tu aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8085"]
