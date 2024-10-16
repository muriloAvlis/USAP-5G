cmake_minimum_required(VERSION 3.15)
project(xapp_usap VERSION 0.0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_C_FLAGS_RELEASE "-O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

## For FlexRIC build
set(UNIT_TEST "FALSE" CACHE STRING "build test cases") ## It's need to disable this for compilation to work
set(E2AP_VERSION "E2AP_V3" CACHE STRING "E2AP version")
set(KPM_VERSION "KPM_V3_00" CACHE STRING "The KPM SM version to use")
set(XAPP_MULTILANGUAGE OFF CACHE BOOL "xApp multilanguage support")

## For pb
set(ABSL_PROPAGATE_CXX_STD ON)


## Definitions
add_compile_definitions(SPDLOG_ACTIVE_LEVEL)

## Import libs
find_package(Protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)
find_package(spdlog REQUIRED)

## BUILD EXTERNAL LIBS
Include(FetchContent)

## FlexRIC
FetchContent_Declare(
        flexric
        GIT_REPOSITORY https://gitlab.eurecom.fr/mosaic5g/flexric.git
        GIT_TAG        dev
)

## SPDLOG
#FetchContent_Declare(
#        spdlog
#        GIT_REPOSITORY https://github.com/gabime/spdlog.git
#        GIT_TAG v1.14.1
#)

## Protobuf
#FetchContent_Declare(
#        pb
#        GIT_REPOSITORY https://github.com/protocolbuffers/protobuf.git
#        GIT_TAG v28.2
#)

## gRPC
#FetchContent_Declare(
#        grpc
#        GIT_REPOSITORY https://github.com/grpc/grpc.git
#        GIT_TAG v1.67.0
#)

FetchContent_MakeAvailable(flexric)

## Config executable
add_executable(xapp_usap
        src/xapp_usap.cpp
        src/e2sm/kpm_monitor.cpp
        src/e2sm/kpm_monitor.hpp
        includes/defer.hpp
        src/utils/utils.cpp
        src/utils/utils.hpp
        src/server/server.cpp
        src/server/server.hpp
)

## Generate gRPC and proto files
set(PROTO_FILE "${CMAKE_CURRENT_SOURCE_DIR}/protobuf/xapp.proto")
set(PROTO_OUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/pb")

protobuf_generate(
        TARGET xapp_usap
        PROTOS ${PROTO_FILE}
        PROTOC_OUT_DIR "${PROTO_OUT_DIR}"
)

protobuf_generate(
        TARGET xapp_usap
        LANGUAGE grpc
        GENERATE_EXTENSIONS .grpc.pb.h .grpc.pb.cc
        PLUGIN "protoc-gen-grpc=\$<TARGET_FILE:gRPC::grpc_cpp_plugin>"
        PROTOS ${PROTO_FILE}
        PROTOC_OUT_DIR "${PROTO_OUT_DIR}"
)

target_include_directories(xapp_usap PUBLIC
        ${flexric_SOURCE_DIR}/src/xApp/
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_CURRENT_SOURCE_DIR}/includes/
        ${PROTO_OUT_DIR}
)

target_link_libraries(xapp_usap PUBLIC
        e42_xapp
        spdlog::spdlog $<$<BOOL:${MINGW}>:ws2_32>
        protobuf::libprotobuf
        gRPC::grpc++
        -pthread
        -lsctp
        -ldl
)