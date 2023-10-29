### Notes:
This is the api module. It is responsible for handling all requests to the server. It is built on top of FastAPI.
The structure and code of the api module is based heavily on the FastAPI tutorial, as well as the Full Stack FastAPI and PostgreSQL - Base Project Generator:
The tutorial can be found here:
https://fastapi.tiangolo.com/tutorial/

The base project generator can be found here:
https://github.com/tiangolo/full-stack-fastapi-postgresql

### Setup:
To setup the api module, you must first install the requirements. This can be done by running the following command:
```
pip install -r requirements.txt
```

### Running:
To run the api module, you must first run the following command:
```
uvicorn main:app --reload
```
This will start the server on port 8000. You can then access the api at http://localhost:8000

#### NOTE:
If you get an module not found error:
```
cd in the api directory and run the following command:
```
```
uvicorn app.main:app --reload
```

### Structure:
The api module is structured as follows:
```
api
├───app
│   ├───api
│   │   ├───endpoints
│   │   │

The models folder contains the tables for the database including the types of each column to build the database.
the schemas folder contains the pydantic models for the api endpoints. These are used to validate the data sent to the server.
The crud folder contains the functions that are used to interact with the database.

### Alembic:
alembic revision --autogenerate -m "Your Comment"
alembic upgrade head

Links:

Annotations:
https://fastapi.tiangolo.com/tutorial/response-model/

Json Encoder:
https://fastapi.tiangolo.com/tutorial/encoder/
