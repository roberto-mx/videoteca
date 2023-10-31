FROM python:3.9

WORKDIR /app

# Instala Jav
RUN apt-get update && apt-get install -y openjdk-11-jre

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8085

CMD ["python", "manage.py", "runserver", "0.0.0.0:8085"]
    