# CMake from https://github.com/Mizux/dotnet-native LICENSE: Apache License 2.0
if(NOT BUILD_DOTNET)
  return()
endif()
# Will need swig
set(CMAKE_SWIG_FLAGS)
find_package(SWIG REQUIRED)
include(UseSWIG)

# if(${SWIG_VERSION} VERSION_GREATER_EQUAL 4) list(APPEND CMAKE_SWIG_FLAGS
# "-doxygen") endif()

if(UNIX AND NOT APPLE)
  list(APPEND CMAKE_SWIG_FLAGS "-DSWIGWORDSIZE64")
endif()

# Find dotnet cli
find_program(DOTNET_EXECUTABLE NAMES dotnet)
if(NOT DOTNET_EXECUTABLE)
  message(FATAL_ERROR "Check for dotnet Program: not found")
else()
  message(STATUS "Found dotnet Program: ${DOTNET_EXECUTABLE}")
endif()

# Create the native library
add_library(cspy-dotnet-native SHARED "")
set_target_properties(cspy-dotnet-native
                      PROPERTIES PREFIX "" POSITION_INDEPENDENT_CODE ON)
# note: macOS is APPLE and also UNIX !
if(APPLE)
  set_target_properties(cspy-dotnet-native PROPERTIES INSTALL_RPATH
                                                      "@loader_path")
  # Xcode fails to build if library doesn't contains at least one source file.
  if(XCODE)
    file(
      GENERATE
      OUTPUT ${PROJECT_BINARY_DIR}/cspy-dotnet-native/version.cpp
      CONTENT "namespace {char* version = \"${PROJECT_VERSION}\";}")
    target_sources(cspy-dotnet-native
                   PRIVATE ${PROJECT_BINARY_DIR}/cspy-dotnet-native/version.cpp)
  endif()
elseif(UNIX)
  set_target_properties(cspy-dotnet-native PROPERTIES INSTALL_RPATH "$ORIGIN")
endif()

list(APPEND CMAKE_SWIG_FLAGS ${FLAGS} "-I${PROJECT_SOURCE_DIR}")

# Needed by dotnet/CMakeLists.txt
set(DOTNET_PACKAGE cspy.DN)
set(DOTNET_PACKAGES_DIR "${PROJECT_BINARY_DIR}/dotnet/packages")
if(APPLE)
  set(RUNTIME_IDENTIFIER osx-x64)
elseif(UNIX)
  set(RUNTIME_IDENTIFIER linux-x64)
elseif(WIN32)
  set(RUNTIME_IDENTIFIER win-x64)
else()
  message(FATAL_ERROR "Unsupported system !")
endif()
set(DOTNET_NATIVE_PROJECT ${DOTNET_PACKAGE}.runtime.${RUNTIME_IDENTIFIER})
set(DOTNET_PROJECT ${DOTNET_PACKAGE})

# Swig wrap all libraries
add_subdirectory(src/cc/dotnet)
target_link_libraries(cspy-dotnet-native PRIVATE BiDirectionalDotnet)

file(COPY dotnet/logo.png DESTINATION dotnet)
set(DOTNET_LOGO_DIR "${PROJECT_BINARY_DIR}/dotnet")
configure_file(dotnet/Directory.Build.props.in dotnet/Directory.Build.props)

# ##############################################################################
# .Net Runtime Package  ##
# ##############################################################################
message(STATUS ".Net runtime project: ${DOTNET_NATIVE_PROJECT}")
set(DOTNET_NATIVE_PATH ${PROJECT_BINARY_DIR}/dotnet/${DOTNET_NATIVE_PROJECT})
message(STATUS ".Net runtime project build path: ${DOTNET_NATIVE_PATH}")

# *.csproj.in contains: CMake variable(s) (@PROJECT_NAME@) that configure_file()
# can manage and generator expression ($<TARGET_FILE:...>) that file(GENERATE)
# can manage.
configure_file(${PROJECT_SOURCE_DIR}/dotnet/${DOTNET_PACKAGE}.runtime.csproj.in
               ${DOTNET_NATIVE_PATH}/${DOTNET_NATIVE_PROJECT}.csproj.in @ONLY)
file(
  GENERATE
  OUTPUT ${DOTNET_NATIVE_PATH}/$<CONFIG>/${DOTNET_NATIVE_PROJECT}.csproj.in
  INPUT ${DOTNET_NATIVE_PATH}/${DOTNET_NATIVE_PROJECT}.csproj.in)

add_custom_command(
  OUTPUT ${DOTNET_NATIVE_PATH}/${DOTNET_NATIVE_PROJECT}.csproj
  DEPENDS ${DOTNET_NATIVE_PATH}/$<CONFIG>/${DOTNET_NATIVE_PROJECT}.csproj.in
  COMMAND
    ${CMAKE_COMMAND} -E copy ./$<CONFIG>/${DOTNET_NATIVE_PROJECT}.csproj.in
    ${DOTNET_NATIVE_PROJECT}.csproj
  WORKING_DIRECTORY ${DOTNET_NATIVE_PATH})

add_custom_target(
  dotnet_native_package
  DEPENDS ${DOTNET_NATIVE_PATH}/${DOTNET_NATIVE_PROJECT}.csproj
  COMMAND ${CMAKE_COMMAND} -E make_directory packages
  COMMAND ${DOTNET_EXECUTABLE} build -c Release
          ${DOTNET_NATIVE_PROJECT}/${DOTNET_NATIVE_PROJECT}.csproj
  COMMAND ${DOTNET_EXECUTABLE} pack -c Release
          ${DOTNET_NATIVE_PROJECT}/${DOTNET_NATIVE_PROJECT}.csproj
  BYPRODUCTS dotnet/${DOTNET_NATIVE_PROJECT}/bin
             dotnet/${DOTNET_NATIVE_PROJECT}/obj
  WORKING_DIRECTORY dotnet)
add_dependencies(dotnet_native_package cspy-dotnet-native)

# ##############################################################################
# .Net Package  ##
# ##############################################################################
message(STATUS ".Net project: ${DOTNET_PROJECT}")
set(DOTNET_PATH ${PROJECT_BINARY_DIR}/dotnet/${DOTNET_PROJECT})
message(STATUS ".Net project build path: ${DOTNET_PATH}")

configure_file(${PROJECT_SOURCE_DIR}/dotnet/${DOTNET_PROJECT}.csproj.in
               ${DOTNET_PATH}/${DOTNET_PROJECT}.csproj.in @ONLY)

add_custom_command(
  OUTPUT ${DOTNET_PATH}/${DOTNET_PROJECT}.csproj
  DEPENDS ${DOTNET_PATH}/${DOTNET_PROJECT}.csproj.in
  COMMAND ${CMAKE_COMMAND} -E copy ${DOTNET_PROJECT}.csproj.in
          ${DOTNET_PROJECT}.csproj
  WORKING_DIRECTORY ${DOTNET_PATH})

add_custom_target(
  dotnet_package ALL
  DEPENDS ${DOTNET_PATH}/${DOTNET_PROJECT}.csproj
  COMMAND ${DOTNET_EXECUTABLE} build -c Release
          ${DOTNET_PROJECT}/${DOTNET_PROJECT}.csproj
  COMMAND ${DOTNET_EXECUTABLE} pack -c Release
          ${DOTNET_PROJECT}/${DOTNET_PROJECT}.csproj
  BYPRODUCTS dotnet/${DOTNET_PROJECT}/bin dotnet/${DOTNET_PROJECT}/obj
             dotnet/packages
  WORKING_DIRECTORY dotnet)
add_dependencies(dotnet_package dotnet_native_package)

# ##############################################################################
# .Net Test  ##
# ##############################################################################
# add_dotnet_test() CMake function to generate and build dotnet test.
# Parameters: the dotnet filename e.g.: add_dotnet_test(FooTests.cs)
function(add_dotnet_test FILE_NAME)
  message(STATUS "Configuring test ${FILE_NAME} ...")
  get_filename_component(TEST_NAME ${FILE_NAME} NAME_WE)

  set(DOTNET_TEST_PATH ${PROJECT_BINARY_DIR}/dotnet/${TEST_NAME})
  message(STATUS "build path: ${DOTNET_TEST_PATH}")
  file(MAKE_DIRECTORY ${DOTNET_TEST_PATH})

  file(COPY ${FILE_NAME} DESTINATION ${DOTNET_TEST_PATH})

  set(DOTNET_PACKAGES_DIR "${PROJECT_BINARY_DIR}/dotnet/packages")
  configure_file(${PROJECT_SOURCE_DIR}/dotnet/Test.csproj.in
                 ${DOTNET_TEST_PATH}/${TEST_NAME}.csproj @ONLY)

  add_custom_target(
    dotnet_test_${TEST_NAME} ALL
    DEPENDS ${DOTNET_TEST_PATH}/${TEST_NAME}.csproj
    COMMAND ${DOTNET_EXECUTABLE} build -c Release
    BYPRODUCTS ${DOTNET_TEST_PATH}/bin ${DOTNET_TEST_PATH}/obj
    WORKING_DIRECTORY ${DOTNET_TEST_PATH})
  add_dependencies(dotnet_test_${TEST_NAME} dotnet_package)

  if(BUILD_TESTING)
    add_test(
      NAME dotnet_${TEST_NAME}
      COMMAND ${DOTNET_EXECUTABLE} test --no-build -c Release
      WORKING_DIRECTORY ${DOTNET_TEST_PATH})
  endif()

  message(STATUS "Configuring test ${FILE_NAME} done")
endfunction()

if(BUILD_TESTING)
  add_subdirectory(test/dotnet/)
endif()
