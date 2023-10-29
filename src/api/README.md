<!-- omit from toc -->
## API Description
This is the api module. It is responsible for handling all requests to the server. It is built on top of FastAPI.
The structure and code of the api module is based heavily on the FastAPI tutorial, as well as the Full Stack FastAPI and PostgreSQL - Base Project Generator:
The tutorial can be found here:
https://fastapi.tiangolo.com/tutorial/

The base project generator can be found here:
https://github.com/tiangolo/full-stack-fastapi-postgresql

<!-- omit from toc -->
## Table of contents:
- [Setup:](#setup)
- [Running:](#running)
  - [NOTE:](#note)
- [Structure:](#structure)
- [Alembic (DB migrations):](#alembic-db-migrations)
  - [Alembic with geoalchemy2:](#alembic-with-geoalchemy2)
- [Links:](#links)


## Setup:
To setup the api module, you must first install the requirements. This can be done by running the following command:
```
pip install -r requirements.txt
```

## Running:
To run the api module, you must first run the following command:
```
uvicorn main:app --reload
```
This will start the server on port 8000. You can then access the api at http://localhost:8000

### NOTE:
If you get an *'module not found'* error:

*'cd'* in the api directory and run the following command:

```
uvicorn app.main:app --reload
```

## Structure:
The api module is structured as follows:
```
api
├───app
│   ├───api
│   │   ├───endpoints
│   │   │
```
The models folder contains the tables for the database including the types of each column to build the database.
the schemas folder contains the pydantic models for the api endpoints. These are used to validate the data sent to the server.
The crud folder contains the functions that are used to interact with the database.

## Alembic (DB migrations):
Go to the api directory and run the following commands:

```
alembic revision --autogenerate -m "Your Comment"
```
To generate a new migration file. Then run:
```
alembic upgrade head
```
To apply the migration to the database.\
To downgrade the database, run:
```
alembic downgrade -1
```
or
```
alembic downgrade base
```
### Alembic with geoalchemy2:
Docs for geoalchemy2 with alembic:
https://geoalchemy-2.readthedocs.io/en/latest/alembic.html

## Links:

Annotations:
https://fastapi.tiangolo.com/tutorial/response-model/

Json Encoder:
https://fastapi.tiangolo.com/tutorial/encoder/
