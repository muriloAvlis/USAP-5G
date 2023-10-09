FROM golang:1.21.1 as build

ENV XAPPNAME=qmai
WORKDIR /usr/src/github.com/muriloAvlis/qmai/
COPY ../go.mod ../go.sum ./
RUN go mod download && go mod verify
COPY ../ .
RUN go build -v -o ./build/_output/${XAPPNAME} ./cmd/${XAPPNAME}

FROM alpine:3.18

# RUN apk add libc6-compat
USER nobody
COPY --from=build /usr/src/github.com/muriloAvlis/qmai/build/_output/qmai /usr/local/bin/qmai
ENTRYPOINT ["qmai"]