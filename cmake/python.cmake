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
  python/setup.py.in
  ${CMAKE_CURRENT_BINARY_DIR}/python/setup.py.in
  @ONLY)
file(GENERATE
	OUTPUT python/$<CONFIG>/setup.py
  INPUT ${CMAKE_CURRENT_BINARY_DIR}/python/setup.py.in)

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
  add_custom_target(python_package ALL
	# Create appropriate package structure
    COMMAND ${CMAKE_COMMAND} -E make_directory ${PROJECT_NAME} ${PROJECT_NAME}/.libs ${PROJECT_NAME}/algorithms/
	# Copy setup generated file
    COMMAND ${CMAKE_COMMAND} -E copy $<CONFIG>/setup.py setup.py
	# Copy python source code
    COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/src/python/* ${PROJECT_NAME}/
  	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/src/python/algorithms/* ${PROJECT_NAME}/algorithms/
    COMMAND ${CMAKE_COMMAND} -E remove_directory dist
    COMMAND ${CMAKE_COMMAND} -E make_directory ${PROJECT_NAME}/.libs
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:pyBiDirectionalCpp> ${PROJECT_NAME}/algorithms/
    # Don't need to copy static lib on Windows
    COMMAND ${CMAKE_COMMAND} -E $<IF:$<BOOL:${UNIX}>,copy,true> $<TARGET_FILE:BiDirectionalCpp> ${PROJECT_NAME}/.libs
  	# copy swig generated python interface file
  	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/python/*.py ${PROJECT_NAME}/algorithms/
  	# Install prereqs for testing
	COMMAND ${Python_EXECUTABLE} -m pip install -r ${PROJECT_SOURCE_DIR}/python/requirements.dev.txt
    # Build wheel
    COMMAND ${Python_EXECUTABLE} setup.py sdist bdist_wheel
    # Remove setup.py (otherwise will be called again when installing
	# COMMAND ${CMAKE_COMMAND} -E remove setup.py
  	# Must not call it in a folder containing the setup.py otherwise pip call it
  	# (i.e. "python setup.py bdist") while we want to consume the wheel package
	COMMAND pip3 install --user ${PROJECT_SOURCE_DIR}/build/python/dist/*.whl
	# Copy setup generated file (again for release)
	# COMMAND ${CMAKE_COMMAND} -E copy $<CONFIG>/setup.py setup.py
    BYPRODUCTS
    python/${PROJECT_NAME}
    python/build
    python/dist
    python/${PROJECT_NAME}.egg-info
    WORKING_DIRECTORY python
    )
  # Test to be run from build/
  add_test(NAME python_unittest
	COMMAND ${Python_EXECUTABLE} -m unittest discover -s ../test/python/)
endif()

if (CMAKE_BUILD_TYPE EQUAL "Release")
  # TODO
endif()
