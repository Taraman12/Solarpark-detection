Build docker
```bash
docker build -t api-ml-serve -f .dockerfile .
```

Run docker
```bash
docker run -p 8080:8080 --expose 8080 --network=mynetwork --name ml-serve api-ml-serve
```

Tag container
```bash
docker tag api-ml-serve:latest taraman12/api-ml-serve:latest
```

Push container
```bash
docker push taraman12/api-ml-serve:latest
```
