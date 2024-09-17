cmake_minimum_required(VERSION 3.15)

project(usap-xapp VERSION 1.0.0 LANGUAGES C)

## Building parameters
set(CMAKE_C_FLAGS_RELEASE "-O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

add_subdirectory(xapp)