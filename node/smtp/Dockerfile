FROM node:alpine
WORKDIR /node/app
COPY package.json smtp-server.js ./
RUN npm i
ENTRYPOINT [ "node" ]
CMD ["smtp-server.js"]
EXPOSE 2525