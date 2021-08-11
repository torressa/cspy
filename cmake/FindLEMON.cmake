message(STATUS "Trying to find lemon")

if(UNIX)
  set(LEMON_ROOT_DIR
      "/usr/local"
      CACHE PATH "LEMON root directory")
else()
  set(LEMON_ROOT_DIR
      "C:/Program Files (x86)/LEMON/"
      CACHE PATH "LEMON root directory")
endif(UNIX)

find_path(LEMON_INCLUDE_DIR lemon/core.h
          HINTS ${LEMON_ROOT_DIR}/include
                "C:/Program Files (x86)/LEMON/include")
find_library(
  LEMON_LIBRARY
  NAMES lemon emon
  HINTS ${LEMON_ROOT_DIR}/lib "C:/Program Files (x86)/LEMON/lib")

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(LEMON DEFAULT_MSG LEMON_LIBRARY
                                  LEMON_INCLUDE_DIR)

if(LEMON_FOUND)
  message(STATUS "Found LEMON: ${LEMON_INCLUDE_DIR}")
  set(LEMON_INCLUDE_DIRS ${LEMON_INCLUDE_DIR})
  set(LEMON_LIBRARIES ${LEMON_LIBRARY})
endif(LEMON_FOUND)

# mark_as_advanced(LEMON_LIBRARY LEMON_INCLUDE_DIR)

add_library(lemon INTERFACE)
add_library(lemon::lemon ALIAS lemon)
target_include_directories(lemon INTERFACE ${LEMON_INCLUDE_DIRS})
target_link_libraries(lemon INTERFACE ${LEMON_LIBRARIES})

# Install
include(GNUInstallDirs)
install(
  TARGETS lemon
  EXPORT ${PROJECT_NAME}Targets
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/lemon
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} # RUNTIME DESTINATION
          # ${CMAKE_INSTALL_BINDIR}
)
