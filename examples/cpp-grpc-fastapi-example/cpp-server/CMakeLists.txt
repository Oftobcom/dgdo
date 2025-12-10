cmake_minimum_required(VERSION 3.15)
project(helloworld_grpc)

find_package(Protobuf REQUIRED)
find_package(gRPC CONFIG REQUIRED)

include_directories(${Protobuf_INCLUDE_DIRS})

add_executable(greeter_server main.cpp helloworld.pb.cc helloworld.grpc.pb.cc)
target_link_libraries(greeter_server
  gRPC::grpc++
  ${Protobuf_LIBRARIES}
)
