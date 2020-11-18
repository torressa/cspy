set(NAME BiDirectional_test)

file(GLOB _SRCS "src/*")

add_executable(${NAME}
  src/main.cc
  src/test_labelling.cc
  src/test_bidirectional.cc
  src/test_issue17.cc
  src/test_issue22.cc
  src/test_issue38.cc
  src/test_issue52.cc
  # src/test_benchmarks.cc
  )
# note: macOS is APPLE and also UNIX !
if(APPLE)
  set_target_properties(${NAME} PROPERTIES
    INSTALL_RPATH "@loader_path/../${CMAKE_INSTALL_LIBDIR}")
elseif(UNIX AND NOT APPLE)
  set_target_properties(${NAME} PROPERTIES
    INSTALL_RPATH "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}")
endif()
target_link_libraries(${NAME}
  gtest
  ${PROJECT_NAME}::BiDirectionalCpp)
target_include_directories(${NAME}
  PRIVATE
  ${PROJECT_SOURCE_DIR}/src/cc/
  )

add_test(NAME ${NAME} COMMAND $<TARGET_FILE:${NAME}>)
