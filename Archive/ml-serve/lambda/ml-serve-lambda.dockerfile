FROM public.ecr.aws/lambda/python:3.10

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY config.properties ${LAMBDA_TASK_ROOT}/config.properties

COPY ./model-store ${LAMBDA_TASK_ROOT}/model-store/

# CMD ["torchserve", "--start" ,"--ncs", "--model-store", "/tmp/model-store" ,"--models" ,"solar-park-detection=solar-park-detection.mar"]
COPY app.py ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ]
