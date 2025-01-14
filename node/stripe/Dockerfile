FROM node:alpine
WORKDIR /node/app
COPY package.json ./
COPY ./services ./services
COPY ./frontend ./frontend
RUN npm i
ENTRYPOINT [ "node" ]