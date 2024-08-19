## add -fPIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

file(GLOB KPM_SRC "${CMAKE_CURRENT_SOURCE_DIR}/kpm_v4.00_compiled/*.c")
file(GLOB KPM_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/kpm_v4.00_compiled/*.h")

add_library(e2smwrapper SHARED wrapper.c ${KPM_SRC})

target_include_directories(e2smwrapper PUBLIC
        kpm_v4.00_compiled
)

## define PDU macro
target_compile_definitions(e2smwrapper PRIVATE -DPDU)
## link libm
target_link_libraries(e2smwrapper PUBLIC m)

install(TARGETS e2smwrapper ARCHIVE DESTINATION lib)
install(FILES wrapper.h ${KPM_HEADERS} ${INCLUDE_HEADERS} DESTINATION include/e2sm)