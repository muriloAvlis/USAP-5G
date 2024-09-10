## Source test
add_executable(testAsn1Coder testAsn1Coder.c)

## Add lib
target_link_libraries(testAsn1Coder PUBLIC asn1coder)

## Add headers
target_include_directories(testAsn1Coder PUBLIC ../src)

## Add Ctest
add_test(NAME Asn1CoderTest COMMAND testAsn1Coder)