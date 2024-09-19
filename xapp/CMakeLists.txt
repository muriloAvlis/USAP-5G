cmake_minimum_required(VERSION 3.15)

project(usap-xapp VERSION 1.0.0 LANGUAGES CXX)

## Building parameters
set(CMAKE_C_FLAGS_RELEASE "-O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

## FlexRIC lib
add_subdirectory(libs)

## xApp source files
set(SOURCE_FILES
        src/usap.cpp
        src/grpc_server.cpp
)
## xApp header files
set(HEADER_FILES
        src/usap.hpp
        src/grpc_server.hpp
        src/defer.hpp
)

## xApp lib
add_executable(xapp_usap
        ${SOURCE_FILES}
        ${HEADER_FILES}
)

## Find dependencies
find_package(gRPC REQUIRED)
find_package(Protobuf REQUIRED)

#### Build pb file ####
set(PROTO_FILES ${CMAKE_CURRENT_SOURCE_DIR}/pb/xapp.proto)
## Set pb output directory
set(PROTO_BINARY_DIR "${CMAKE_CURRENT_BINARY_DIR}")
## Generate Protobuf files
protobuf_generate_cpp(
        PROTO_SRCS PROTO_HDRS
        TARGET xapp_usap
        PROTOC_OUT_DIR ${PROTO_BINARY_DIR}
        PROTOS ${PROTO_FILES}
)

## Generate gRPC files
protobuf_generate(
        TARGET xapp_usap
        LANGUAGE grpc
        GENERATE_EXTENSIONS .grpc.pb.h .grpc.pb.cc
        PLUGIN "protoc-gen-grpc=\$<TARGET_FILE:gRPC::grpc_cpp_plugin>"
        PROTOC_OUT_DIR ${PROTO_BINARY_DIR}
        PROTOS ${PROTO_FILES}
)

## link header files
target_include_directories(xapp_usap
        PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_CURRENT_SOURCE_DIR}/libs
        ${PROTO_BINARY_DIR}  # Include generated protobuf headers
)

## link libraries
target_link_libraries(xapp_usap
        PUBLIC
        e42_xapp
        gRPC::grpc++
        protobuf::libprotobuf
        -pthread
        -lsctp
        -ldl
)

## install xApp binary
install(TARGETS xapp_usap ARCHIVE DESTINATION bin)