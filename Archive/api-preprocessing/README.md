Build docker
```bash
docker build -t api-preprocessing -f .dockerfile .
```

Run docker
```bash
docker run -p 8000:8000 --expose 8000 --network=mynetwork --name preprocessing api-preprocessing
```

Tag container
```bash
docker tag api-preprocessing:latest taraman12/api-preprocessing:latest
```

Push container
```bash
docker push taraman12/api-preprocessing:latest
```
