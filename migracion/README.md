# Metadata generator

## Overview
This project help to get a DDL or a SQLAlchemy model from csv files of a dumped database

## Requirements
Python 3.5.2+

## Virtual environment
To create a virtual environment on Windows, use:
```
python3 -m venv venv
venv\Scripts\activate
```

On mac, use:
```
python3 -m venv venv
source venv/bin/activate
```

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt

set FLASK_ENV=development
set FLASK_DEBUG=1
flask run
```

Useful commands:

```
pip freeze > requirements.txt
```