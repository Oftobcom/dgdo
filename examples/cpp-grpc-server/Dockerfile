FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    build-essential cmake \
    protobuf-compiler protobuf-compiler-grpc \
    libprotobuf-dev libgrpc++-dev

WORKDIR /app

COPY . .

RUN mkdir build && cd build && \
    cmake .. && \
    make -j4

EXPOSE 50051

CMD ["./build/server"]
