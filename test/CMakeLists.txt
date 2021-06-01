cmake_minimum_required(VERSION 2.8.7)

############################################
# Run the tests
############################################

configure_file( ${CMAKE_CURRENT_SOURCE_DIR}/test.py
                ${CMAKE_CURRENT_BINARY_DIR}/../test.py COPYONLY)

add_custom_target(
    RUN_TESTSUITE
    COMMAND python3 test.py
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/.."
    DEPENDS ${MODULES}
    COMMENT "Running test suite..."
)
