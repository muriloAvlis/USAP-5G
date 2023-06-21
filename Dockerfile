FROM golang:1.20.5-alpine

WORKDIR /root

COPY . .

RUN go get github.com/onosproject/onos-ric-sdk-go

RUN go build -v -o /usr/local/bin/qmai main.go

ENTRYPOINT ["qmai"]