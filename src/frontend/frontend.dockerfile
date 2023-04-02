FROM node:18.15.0-bullseye-slim

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

EXPOSE 8080

CMD [ "npm", "run" ,"dev", "--", "--host", "--port", "8080"]
