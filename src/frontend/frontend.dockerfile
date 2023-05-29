FROM node:18.15.0-bullseye-slim

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

RUN chmod +x /app/vite.config.ts
# needed for depolyment on aws
RUN chmod -R a+x /app/node_modules

EXPOSE 5000

# change to production for production
CMD [ "npm", "run" ,"dev", "--", "--host", "--port", "5000"]
