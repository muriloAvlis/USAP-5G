FROM golang:1.21-alpine

WORKDIR /usr/src/qmai

COPY ../go.mod ../go.sum ./
RUN go mod download && go mod verify

COPY ../ .
RUN go build -v -o /usr/local/bin/qmai ./cmd/main.go

ENTRYPOINT ["qmai"]