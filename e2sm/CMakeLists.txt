add_library(e2smwrapper STATIC wrapper.c)

target_include_directories(e2smwrapper PUBLIC
        kpm_v4.00_compiled
        ../include
)

file(GLOB KPM_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/kpm_v4.00_compiled/*.h")
file(GLOB INCLUDE_HEADERS "../include/*.h")

install(TARGETS e2smwrapper ARCHIVE DESTINATION lib)
install(FILES wrapper.h ${KPM_HEADERS} ${INCLUDE_HEADERS} DESTINATION include/e2sm)