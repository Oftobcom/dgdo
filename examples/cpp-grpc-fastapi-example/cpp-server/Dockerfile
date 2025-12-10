# Stage 1: build deps, protoc, gRPC, compile server
FROM ubuntu:22.04 AS builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git autoconf libtool pkg-config \
    wget unzip ca-certificates python3 python3-pip

# Install protobuf (build from source)
WORKDIR /opt
RUN git clone --depth 1 -b v23.6 https://github.com/protocolbuffers/protobuf.git \
 && cd protobuf && git submodule update --init --recursive \
 && mkdir -p cmake/build && cd cmake/build \
 && cmake ../.. -Dprotobuf_BUILD_TESTS=OFF \
 && make -j$(nproc) && make install \
 && ldconfig

# Install gRPC (build from source)
WORKDIR /opt
RUN git clone --depth 1 -b v1.57.0 https://github.com/grpc/grpc \
 && cd grpc && git submodule update --init --recursive \
 && mkdir -p cmake/build && cd cmake/build \
 && cmake ../.. -DgRPC_BUILD_TESTS=OFF -DgRPC_INSTALL=ON \
 && make -j$(nproc) && make install \
 && ldconfig

# Copy project
WORKDIR /workspace
COPY ../proto /workspace/proto
COPY . /workspace

# Generate C++ sources from proto
RUN protoc --proto_path=/workspace/proto \
    --cpp_out=/workspace \
    --grpc_out=/workspace --plugin=protoc-gen-grpc=$(which grpc_cpp_plugin) \
    /workspace/proto/helloworld.proto

# Build server with CMake
WORKDIR /workspace
RUN apt-get install -y --no-install-recommends cmake \
 && mkdir -p build && cd build \
 && cmake .. \
 && make -j$(nproc)

# Stage 2: runtime
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /workspace/build/greeter_server /usr/local/bin/greeter_server
EXPOSE 50051
ENTRYPOINT ["/usr/local/bin/greeter_server"]
