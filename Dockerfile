FROM python:3.9

WORKDIR /app

# Instala OpenJDK 11
RUN apt-get update && apt-get install -y openjdk-11-jre-headless

# Configura JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Elimina los paquetes de Java
RUN apt-get remove -y openjdk-11-jre-headless && apt-get autoremove -y

EXPOSE 8085

CMD ["python", "manage.py", "runserver", "0.0.0.0:8085"]
