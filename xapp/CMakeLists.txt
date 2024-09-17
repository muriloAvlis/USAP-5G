## FlexRIC lib
add_subdirectory(libs)

## xApp lib
add_library(xapp_usap SHARED
        ./src/usap.c
)

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