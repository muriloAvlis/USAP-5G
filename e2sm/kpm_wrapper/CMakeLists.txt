## add -fPIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

file(GLOB KPM_ENCODER_SRC "${CMAKE_CURRENT_SOURCE_DIR}/lib/*.c")
file(GLOB KPM_ENCODER_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/lib/*.h")

add_library(e2sm_kpm_encoder SHARED src/wrapper.c ${KPM_ENCODER_SRC})

target_include_directories(e2sm_kpm_encoder PUBLIC
        lib
)

## define PDU macro
target_compile_definitions(e2sm_kpm_encoder PUBLIC -DPDU)
## link libm
target_link_libraries(e2sm_kpm_encoder PUBLIC m)

install(TARGETS e2sm_kpm_encoder ARCHIVE DESTINATION lib)
install(FILES src/wrapper.h ${KPM_ENCODER_HEADERS} DESTINATION include/e2sm/kpm_encoder)