FROM golang:1.22.0 as build

ENV XAPPNAME=qmai
WORKDIR /usr/src/github.com/muriloAvlis/qmai/
COPY ../go.mod ../go.sum ./
RUN go mod download && go mod verify
COPY ../ .
RUN go build -v -o ./build/_output/${XAPPNAME} ./cmd/${XAPPNAME}

FROM alpine:3.19
# TODO: creates appConfig path
RUN apk add libc6-compat
USER nobody
COPY --from=build /usr/src/github.com/muriloAvlis/qmai/build/_output/qmai /usr/local/bin/qmai
ENTRYPOINT ["qmai"]