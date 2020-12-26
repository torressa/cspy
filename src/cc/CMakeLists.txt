add_library(BiDirectionalCpp "")

target_sources(BiDirectionalCpp
  PRIVATE
   bidirectional.cc
   digraph.cc
   labelling.cc
   preprocessing.cc
   ref_callback.cc
   search.cc
   )
target_include_directories(BiDirectionalCpp
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>)

target_compile_features(BiDirectionalCpp PUBLIC cxx_std_17)

set_target_properties(BiDirectionalCpp
	PROPERTIES
	CXX_EXTENSIONS TRUE
	VERSION ${PROJECT_VERSION})

#target_link_libraries(BiDirectionalCpp PUBLIC ...)

add_library(${PROJECT_NAME}::BiDirectionalCpp ALIAS BiDirectionalCpp)

# Install
include(GNUInstallDirs)
install(TARGETS BiDirectionalCpp
  EXPORT ${PROJECT_NAME}Targets
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bidirectional
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  #RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  )
