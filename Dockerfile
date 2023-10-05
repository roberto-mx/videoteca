FROM python:3.9
 
WORKDIR /opt/videoteca

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir myproject

COPY . myproject/

WORKDIR /opt/videoteca/myproject

EXPOSE 8086

CMD ["python", "manage.py", "runserver", "0.0.0.0:8086"]
