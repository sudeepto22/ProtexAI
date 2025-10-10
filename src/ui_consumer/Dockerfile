FROM node:22-alpine

WORKDIR /app

ARG REACT_APP_MQTT_BROKER=ws://localhost:9001
ARG REACT_APP_MQTT_TOPIC=protexai/sensors
ENV REACT_APP_MQTT_BROKER=$REACT_APP_MQTT_BROKER \
    REACT_APP_MQTT_TOPIC=$REACT_APP_MQTT_TOPIC

COPY package.json package-lock.json ./

RUN npm install --legacy-peer-deps --silent

RUN npm i -g serve

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
