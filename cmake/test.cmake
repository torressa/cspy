


add_custom_target(pytest_venv ALL
COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:pyBiDirectionalCpp> ${PROJECT_SOURCE_DIR}/src/bidirectional/
# Don't need to copy static lib on Windows
COMMAND ${CMAKE_COMMAND} -E $<IF:$<BOOL:${UNIX}>,copy,true>
$<TARGET_FILE:BiDirectionalCpp> ${PROJECT_SOURCE_DIR}/src/bidirectional/
COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/python/*.py ${PROJECT_SOURCE_DIR}/src/bidirectional/
COMMAND ${Python_EXECUTABLE} ${PROJECT_SOURCE_DIR}/src/bidirectional/test.py
BYPRODUCTS
WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})
# Clean
add_custom_command(
    OUTPUT .
    COMMAND ${CMAKE_COMMAND} make -C ${PROJECT_SOURCE_DIR}/src/bidirectional/
)
