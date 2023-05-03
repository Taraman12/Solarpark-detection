FROM python:3.10-slim-bullseye

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# only difference is the last main file
CMD ["python", "-m", "app.main_preprocessing"]
