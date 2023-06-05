FROM python:3.10-slim-bullseye

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY app/ .

# only difference is the last main file
CMD ["python", "-m", "main_downloader"]
