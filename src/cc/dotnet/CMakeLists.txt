set_property(SOURCE bidirectional.i PROPERTY CPLUSPLUS ON)
set_property(SOURCE bidirectional.i PROPERTY COMPILE_OPTIONS -dllimport
                                             cspy-dotnet-native)

swig_add_library(
  BiDirectionalDotnet
  TYPE OBJECT
  LANGUAGE csharp OUTPUT_DIR ${PROJECT_BINARY_DIR}/dotnet/${DOTNET_PROJECT}/
  SOURCES bidirectional.i)

set_target_properties(
  BiDirectionalDotnet
  PROPERTIES SWIG_INCLUDE_DIRECTORIES ${PROJECT_SOURCE_DIR}/dotnet
             SWIG_USE_TARGET_INCLUDE_DIRECTORIES ON
             POSITION_INDEPENDENT_CODE ON)

target_link_libraries(BiDirectionalDotnet PRIVATE BiDirectionalCpp LEMON::LEMON)
target_include_directories(BiDirectionalDotnet
                           PRIVATE ${PROJECT_SOURCE_DIR}/src/cc)
