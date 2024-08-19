## add -fPIC
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

file(GLOB KPM_DECODER_SRC "${CMAKE_CURRENT_SOURCE_DIR}/lib/*.c")
file(GLOB KPM_DECODER_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/lib/*.h")

add_library(e2sm_kpm_decoder SHARED src/wrapper.c ${KPM_DECODER_SRC}
        ../kpm_decoder/src/wrapper.c
        ../kpm_decoder/src/wrapper.h)

target_include_directories(e2sm_kpm_decoder PUBLIC
        lib
)

## define PDU macro
target_compile_definitions(e2sm_kpm_decoder PUBLIC -DPDU)
## link libm
target_link_libraries(e2sm_kpm_decoder PUBLIC m)

install(TARGETS e2sm_kpm_decoder ARCHIVE DESTINATION lib)
install(FILES src/wrapper.h ${KPM_DECODER_HEADERS} DESTINATION include/e2sm/kpm_decoder)