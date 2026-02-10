cmake_minimum_required(VERSION 3.10)
project(cpp_grpc_server)

set(CMAKE_CXX_STANDARD 17)

find_package(Protobuf REQUIRED)

set(PROTO_FILE ${CMAKE_SOURCE_DIR}/proto/hello.proto)

# Generate protobuf code
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILE})

# Generate gRPC C++ code
add_custom_command(
    OUTPUT ${CMAKE_BINARY_DIR}/hello.grpc.pb.cc
           ${CMAKE_BINARY_DIR}/hello.grpc.pb.h
    COMMAND ${Protobuf_PROTOC_EXECUTABLE}
    ARGS --grpc_out=${CMAKE_BINARY_DIR}
         --plugin=protoc-gen-grpc=/usr/bin/grpc_cpp_plugin
         -I ${CMAKE_SOURCE_DIR}/proto
         ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
)

set(GRPC_SRCS ${CMAKE_BINARY_DIR}/hello.grpc.pb.cc)
set(GRPC_HDRS ${CMAKE_BINARY_DIR}/hello.grpc.pb.h)

include_directories(
    ${CMAKE_BINARY_DIR}
    ${Protobuf_INCLUDE_DIRS}
    /usr/include
)

add_executable(server
    src/server.cpp
    ${PROTO_SRCS}
    ${PROTO_HDRS}
    ${GRPC_SRCS}
    ${GRPC_HDRS}
)

target_link_libraries(server
    protobuf
    grpc++
    grpc
)
