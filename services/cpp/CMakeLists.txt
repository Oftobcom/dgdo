cmake_minimum_required(VERSION 3.16)
project(matching_server)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Сгенерированные proto-файлы
set(GENERATED_CPP_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../../generated/cpp)

add_executable(matching_server
    matching_server.cpp
    ${GENERATED_CPP_DIR}/matching.pb.cc
    ${GENERATED_CPP_DIR}/matching.grpc.pb.cc
    ${GENERATED_CPP_DIR}/trip_request.pb.cc
    ${GENERATED_CPP_DIR}/trip_request.grpc.pb.cc
    ${GENERATED_CPP_DIR}/trip.pb.cc
    ${GENERATED_CPP_DIR}/trip_service.pb.cc
    ${GENERATED_CPP_DIR}/trip_service.grpc.pb.cc
    ${GENERATED_CPP_DIR}/common.pb.cc
)

target_include_directories(matching_server PRIVATE
    ${GENERATED_CPP_DIR}
)

# Ubuntu-style линковка (БЕЗ find_package(gRPC))
target_link_libraries(matching_server
    grpc++
    grpc
    protobuf
    pthread
)
