cmake_minimum_required(VERSION 3.15)

project(usap-xapp VERSION 1.0.0 LANGUAGES C)

## Building parameters
set(CMAKE_C_FLAGS_RELEASE "-O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# Uninstall target
#if(NOT TARGET uninstall)
#    configure_file(
#            "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
#            "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
#            IMMEDIATE @ONLY)
#
#    add_custom_target(uninstall
#            COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)
#endif()

## xApp development
add_subdirectory(xapp)