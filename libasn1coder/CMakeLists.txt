cmake_minimum_required(VERSION 3.20)

project(ans1coder VERSION 1.0.0 LANGUAGES C)

## add -fPIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# uninstall target
if(NOT TARGET uninstall)
    configure_file(
            "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
            "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
            IMMEDIATE @ONLY)

    add_custom_target(uninstall
            COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)
endif()

file(GLOB E2AP_LIB "${CMAKE_CURRENT_SOURCE_DIR}/libs/e2ap/*.c")
file(GLOB E2AP_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/libs/e2ap/*.h")

add_library(asn1coder SHARED src/asn1coder.c ${KPM_ENCODER_SRC}
        src/asn1coder.c
        src/asn1coder.h)

target_include_directories(asn1coder PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/libs/e2ap
)

## define PDU macro
target_compile_definitions(asn1coder PUBLIC -DPDU)

## link libm
target_link_libraries(asn1coder PUBLIC m)

## Tests
add_subdirectory(test)

install(TARGETS asn1coder ARCHIVE DESTINATION libs)
install(FILES src/asn1coder.h ${E2AP_HEADERS} DESTINATION include/asn1coder)