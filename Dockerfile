# # Utiliza una imagen base de Python (ajusta la versión según tu proyecto)
# FROM python:3.9

# # Instala las dependencias necesarias, como JasperReports
# RUN apt-get update && apt-get install -y jasperreports

# WORKDIR /app

# COPY . /app

# ENV JASPER_REPORTS_DIR /app/jasperreports
# ENV RECURSOS_DIR /app/recursos

# RUN pip install -r requirements.txt

# EXPOSE 8080


# CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]


FROM python:3.9

WORKDIR /app

# Instala OpenJDK usando la opción "default-jre"
RUN apt-get update && apt-get install -y default-jre

# Configura JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8085

CMD ["python", "manage.py", "runserver", "0.0.0.0:8085"]
