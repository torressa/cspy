if(NOT BUILD_CXX)
  return()
endif()

add_subdirectory(src/cc/)
if (BUILD_TESTING)
  include(FetchContent)
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG master)
  set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(googletest)
  add_subdirectory(test_cc/)
endif()

# Install
install(EXPORT cspyTargets
  NAMESPACE cspy::
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/cspy
  COMPONENT Devel)
include(CMakePackageConfigHelpers)
configure_package_config_file(cmake/cspyConfig.cmake.in
  "${PROJECT_BINARY_DIR}/cspyConfig.cmake"
  INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/cspy"
  )
write_basic_package_version_file(
  "${PROJECT_BINARY_DIR}/cspyConfigVersion.cmake"
  COMPATIBILITY SameMajorVersion)
install(
  FILES
  "${PROJECT_BINARY_DIR}/cspyConfig.cmake"
  "${PROJECT_BINARY_DIR}/cspyConfigVersion.cmake"
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/cspy"
  COMPONENT Devel)
