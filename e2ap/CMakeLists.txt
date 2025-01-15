cmake_minimum_required(VERSION 3.15)

project(e2ap VERSION 0.0.1 LANGUAGES C)

## add -fPIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

file(GLOB LIB_SRC "${CMAKE_CURRENT_SOURCE_DIR}/lib/*.c")
file(GLOB LIB_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/lib/*.h")

add_library(e2ap SHARED wrapper.c wrapper.h ${LIB_SRC})

target_include_directories(e2ap PUBLIC
        lib
)

## define PDU macro
target_compile_definitions(e2ap PUBLIC -DPDU)
## link libm
target_link_libraries(e2ap PUBLIC m)

install(TARGETS e2ap ARCHIVE DESTINATION lib)
install(FILES wrapper.h ${LIB_HEADERS} DESTINATION include/e2ap)