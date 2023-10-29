FROM pytorch/torchserve:0.8.1-cpu

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./model-store model-store/

CMD ["torchserve", "--start" ,"--ncs", "--model-store", "model-store" ,"--models" ,"solar-park-detection=solar-park-detection.mar"]
# COPY ./requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r ${LAMBDA_TASK_ROOT}/requirements.txt
# RUN pip uninstall torch torchaudio torchvision -y
# RUN pip install torch==2.0.0+cpu torchvision==0.15.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# COPY config.properties ${LAMBDA_TASK_ROOT}/config.properties
# COPY ./model-store .
# COPY ./model-store ${LAMBDA_TASK_ROOT}/model-store/
# copy the .mar file created in previous step
# COPY app/test_model.mar model-store/
# replace the existing config.properties with custom one
# COPY app/model-store/config.properties /home/model-server/config.properties
# start the server with model named SBERT
# CMD ["torchserve", "--start" ,"--ncs", "--model-store", "/tmp/model-store" ,"--models" ,"solar-park-detection=solar-park-detection.mar"]
#"--ts-config", "app/config.properties"
