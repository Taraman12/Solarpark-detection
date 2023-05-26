FROM python:3.10-slim-bullseye

WORKDIR /app

COPY ./requirements.txt /requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /requirements.txt

COPY ./app /app

# only difference is the last main file
CMD ["python", "-m", "main_preprocessing"]
