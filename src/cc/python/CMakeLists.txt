set_property(SOURCE bidirectional.i PROPERTY CPLUSPLUS ON)
set_property(SOURCE bidirectional.i PROPERTY SWIG_MODULE_NAME pyBiDirectionalCpp)
swig_add_library(pyBiDirectionalCpp
  TYPE SHARED
  LANGUAGE python
  OUTPUT_DIR ${CMAKE_BINARY_DIR}/python/
  SOURCES bidirectional.i)

set_property(TARGET pyBiDirectionalCpp PROPERTY SWIG_USE_TARGET_INCLUDE_DIRECTORIES ON)
target_include_directories(pyBiDirectionalCpp
  PRIVATE
  ../
  ${Python3_INCLUDE_DIRS}
  )

# note: macOS is APPLE and also UNIX !
if(APPLE)
  set_target_properties(pyBiDirectionalCpp PROPERTIES
    SUFFIX ".so"
    INSTALL_RPATH "@loader_path;@loader_path/../../${PROJECT_NAME}/.libs"
    )
  set_property(TARGET pyBiDirectionalCpp APPEND PROPERTY
    LINK_FLAGS "-flat_namespace -undefined suppress"
    )
elseif(UNIX)
  set_target_properties(pyBiDirectionalCpp PROPERTIES
    INSTALL_RPATH "$ORIGIN:$ORIGIN/../../${PROJECT_NAME}/.libs"
    )
endif()
target_link_libraries(pyBiDirectionalCpp PRIVATE BiDirectionalCpp)

# Variable PYTHON_LIBRARIES can contains keyword `optimized`
# which won't be interpreted inside a generator expression.
# i.e. we can't use: $<$<PLATFORM_ID:Windows>:${PYTHON_LIBRARIES}>
# see: https://cmake.org/cmake/help/git-stage/command/target_link_libraries.html#command:target_link_libraries
if(MSVC)
  target_link_libraries(pyBiDirectionalCpp PRIVATE ${Python3_LIBRARIES})
endif()
