add_library(BiDirectionalCpp "")

# Configure
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.h.in
               ${CMAKE_CURRENT_BINARY_DIR}/config.h)

target_sources(
  BiDirectionalCpp PRIVATE bidirectional.cc digraph.cc labelling.cc
                           preprocessing.cc search.cc ref_callback.cc)

target_include_directories(
  BiDirectionalCpp
  PUBLIC $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}>
         $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
         $<BUILD_INTERFACE:${spdlog_SOURCE_DIR}/include>)

target_compile_features(BiDirectionalCpp PUBLIC cxx_std_20)

set_target_properties(BiDirectionalCpp PROPERTIES CXX_EXTENSIONS TRUE
                                                  VERSION ${PROJECT_VERSION})
set_target_properties(
  BiDirectionalCpp
  PROPERTIES CXX_EXTENSIONS TRUE
             VERSION ${PROJECT_VERSION}
             PUBLIC_HEADER "${CMAKE_CURRENT_BINARY_DIR}/config.h"
             VERSION ${PROJECT_VERSION})

target_link_libraries(BiDirectionalCpp PRIVATE LEMON::LEMON)

add_library(${PROJECT_NAME}::BiDirectionalCpp ALIAS BiDirectionalCpp)

# Install
include(GNUInstallDirs)
install(
  TARGETS BiDirectionalCpp
  EXPORT ${PROJECT_NAME}Targets
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bidirectional
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} # RUNTIME DESTINATION
          # ${CMAKE_INSTALL_BINDIR}
)
