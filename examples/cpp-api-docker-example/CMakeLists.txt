cmake_minimum_required(VERSION 3.10)
project(drogon_api CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Drogon and its dependencies
find_package(Drogon REQUIRED)

add_executable(drogon_api main.cc)

# Link Drogon to the executable
target_link_libraries(drogon_api PRIVATE Drogon::Drogon)