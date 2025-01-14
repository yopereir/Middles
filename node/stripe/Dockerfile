FROM node:alpine
WORKDIR /node/app
COPY package.json ./services ./frontend ./
RUN npm i
ENTRYPOINT [ "node" ]