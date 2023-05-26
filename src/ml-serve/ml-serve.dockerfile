FROM pytorch/torchserve:latest-cpu

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./model-store model-store/
#copy the .mar file created in previous step
# COPY app/test_model.mar model-store/
#replace the existing config.properties with custom one
# COPY app/model-store/config.properties /home/model-server/config.properties
#start the server with model named SBERT
CMD ["torchserve", "--start" ,"--ncs", "--model-store", "model-store" ,"--models" ,"solar-park-detection=solar-park-detection.mar"]
#"--ts-config", "app/config.properties"