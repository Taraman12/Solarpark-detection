FROM pytorch/torchserve:0.8.0-cpu

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt
# RUN pip uninstall torch torchaudio torchvision -y
# RUN pip install torch==2.0.0+cpu torchvision==0.15.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

COPY ./model-store model-store/
#copy the .mar file created in previous step
# COPY app/test_model.mar model-store/
#replace the existing config.properties with custom one
# COPY app/model-store/config.properties /home/model-server/config.properties
#start the server with model named SBERT
CMD ["torchserve", "--start" ,"--ncs", "--model-store", "model-store" ,"--models" ,"solar-park-detection=solar-park-detection.mar"]
#"--ts-config", "app/config.properties"