cmake_minimum_required(VERSION 3.10)

project(matching)

set(CMAKE_CXX_STANDARD 17)

add_executable(matching
    src/main.cpp
    src/matcher.cpp
)