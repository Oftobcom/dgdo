# =========================
# Build stage
# =========================
FROM ubuntu:22.04 AS build

ENV DEBIAN_FRONTEND=noninteractive

# ---- system deps ----
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libprotobuf-dev \
    protobuf-compiler \
    libgrpc-dev \
    libgrpc++-dev

# ---- project ----
WORKDIR /app

# копируем ВЕСЬ проект
COPY . /app/dgdo

# ---- build ----
WORKDIR /app/dgdo/services/cpp
RUN mkdir -p build

WORKDIR /app/dgdo/services/cpp/build
RUN cmake .. && make -j$(nproc)

# =========================
# Runtime stage
# =========================
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ---- runtime deps ----
RUN apt-get update && apt-get install -y \
    libprotobuf23 \
    libgrpc++1 \
    libgrpc10

# ---- binary ----
WORKDIR /app
COPY --from=build /app/dgdo/services/cpp/build/matching_server /app/matching_server

EXPOSE 50051

CMD ["/app/matching_server"]
