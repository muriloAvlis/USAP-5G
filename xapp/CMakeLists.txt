## FlexRIC lib
add_subdirectory(libs)

## xApp lib
add_library(xapp_usap SHARED
        ./src/usap.c
)

file(GLOB_RECURSE FLEXRIC_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/libs/flexric/src/*.h")

## link header files
target_include_directories(xapp_usap
        PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_CURRENT_SOURCE_DIR}/libs/flexric/src
)

target_link_libraries(xapp_usap
        PUBLIC
        e42_xapp
        -pthread
        -lsctp
        -ldl
)

install(TARGETS xapp_usap ARCHIVE DESTINATION libs)
install(FILES src/usap.h ${FLEXRIC_HEADERS} DESTINATION include/xapp_usap)