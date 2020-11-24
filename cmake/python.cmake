if(NOT BUILD_PYTHON)
  return()
endif()

# Use latest UseSWIG module
cmake_minimum_required(VERSION 3.14)

if(NOT TARGET cspy::BiDirectionalCpp)
  message(FATAL_ERROR "Python: missing BiDirectional TARGET")
endif()

# Will need swig
set(CMAKE_SWIG_FLAGS)
find_package(SWIG REQUIRED)
include(UseSWIG)

if(${SWIG_VERSION} VERSION_GREATER_EQUAL 4)
  list(APPEND CMAKE_SWIG_FLAGS "-doxygen")
endif()

if(UNIX AND NOT APPLE)
  list(APPEND CMAKE_SWIG_FLAGS "-DSWIGWORDSIZE64")
endif()

# Find Python
find_package(Python REQUIRED COMPONENTS Interpreter Development)

if(Python_VERSION VERSION_GREATER_EQUAL 3)
  list(APPEND CMAKE_SWIG_FLAGS "-py3;-DPY3")
endif()

# Swig wrap all libraries
add_subdirectory(src/cc/python)

#######################
## Python Packaging  ##
#######################
# setup.py.in contains cmake variable e.g. @PROJECT_NAME@ and
# generator expression e.g. $<TARGET_FILE_NAME:labelling>
configure_file(
  setup.py.in
  ${CMAKE_CURRENT_BINARY_DIR}/setup.py.in
  @ONLY)
file(GENERATE
	OUTPUT setup.py
  INPUT ${CMAKE_CURRENT_BINARY_DIR}/setup.py.in)

# Find if python module MODULE_NAME is available,
# if not install it to the Python user install directory.
function(search_python_module MODULE_NAME)
  execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import ${MODULE_NAME}; print(${MODULE_NAME}.__version__)"
    RESULT_VARIABLE _RESULT
    OUTPUT_VARIABLE MODULE_VERSION
    ERROR_QUIET
    OUTPUT_STRIP_TRAILING_WHITESPACE
    )
  if(${_RESULT} STREQUAL "0")
    message(STATUS "Found python module: ${MODULE_NAME} (found version \"${MODULE_VERSION}\")")
  else()
    message(WARNING "Can't find python module \"${MODULE_NAME}\", user install it using pip...")
    execute_process(
      COMMAND ${Python_EXECUTABLE} -m pip install --upgrade --user ${MODULE_NAME}
      OUTPUT_STRIP_TRAILING_WHITESPACE
      )
  endif()
endfunction()


search_python_module(setuptools)
search_python_module(wheel)
# search_python_module(virtualenv)

if(BUILD_TESTING)
  add_custom_target(python_setup ALL
    # Copy and make appropriate folder structure
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/setup.py setup.py
    COMMAND ${CMAKE_COMMAND} -E make_directory .libs cspy
    COMMAND ${CMAKE_COMMAND} -E make_directory cspy/algorithms/
    # Copy cmake output files python and cpp targets
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:pyBiDirectionalCpp> cspy/algorithms/
    # Don't need to copy static lib on Windows
    COMMAND ${CMAKE_COMMAND} -E $<IF:$<BOOL:${UNIX}>,copy,true> $<TARGET_FILE:BiDirectionalCpp> .libs/
    COMMAND ${CMAKE_COMMAND} -E copy src/python/* cspy/
    COMMAND ${CMAKE_COMMAND} -E copy src/python/algorithms/* cspy/algorithms/
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/python/*.py .
    # Install prereqs for testing
    COMMAND ${Python_EXECUTABLE} -m pip install -r requirements.dev.txt
    # Build wheel
    COMMAND ${Python_EXECUTABLE} setup.py bdist_wheel
    # Remove setup.py (otherwise will be called again when installing
    COMMAND ${CMAKE_COMMAND} -E remove setup.py
    # Must not call it in a folder containing the setup.py otherwise pip call it
    # (i.e. "python setup.py bdist") while we want to consume the wheel package
    COMMAND ${Python_EXECUTABLE} -m pip install --find-links=dist ${PROJECT_NAME}
	COMMAND ${Python_EXECUTABLE} -m unittest discover -s test/python/
    BYPRODUCTS
    build
    dist
    ${PROJECT_NAME}.egg-info
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})
  add_test(NAME python_unittest
	COMMAND ${Python_EXECUTABLE} -m unittest discover -s test/python/)
endif()

if (CMAKE_BUILD_TYPE EQUAL "Release")
  # TODO
endif()
