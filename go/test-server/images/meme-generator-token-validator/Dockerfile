FROM golang as build
WORKDIR /usr/src/app
COPY token.go go.mod go.sum ./
RUN go mod download
RUN go build -v -o /usr/local/bin/server ./...
CMD ["server"]