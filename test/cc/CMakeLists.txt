if(BUILD_PYTHON)
  return()
endif()

set(NAME BiDirectional_test)

if(BENCHMARK_TESTS)
  if(BENCHMARK_BOOST)
    find_package(Boost REQUIRED)
    add_executable(${NAME} src/main.cc src/test_benchmarks_boost.cc
                           src/test_benchmarks.cc src/utils.cc)
    target_include_directories(
      ${NAME}
      PUBLIC ${PROJECT_SOURCE_DIR}/src/cc/
             $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
             $<INSTALL_INTERFACE:include> ${Boost_INCLUDE_DIRS})
    target_link_libraries(${NAME} ${Boost_LIBRARIES} gtest
                          ${PROJECT_NAME}::BiDirectionalCpp)
  else()
    add_executable(${NAME} src/main.cc src/test_benchmarks.cc src/utils.cc)
  endif()
else()
  # Unit tests
  add_executable(
    ${NAME}
    src/main.cc
    src/utils.cc
    src/test_labelling.cc
    src/test_bidirectional.cc
    src/test_issue17.cc
    src/test_issue22.cc
    src/test_issue38.cc
    src/test_issue41.cc
    src/test_issue52.cc
    src/test_issue69.cc
    src/test_issue90.cc
    src/test_issue94.cc)
endif()

# note: macOS is APPLE and also UNIX !
if(APPLE)
  set_target_properties(
    ${NAME} PROPERTIES INSTALL_RPATH "@loader_path/../${CMAKE_INSTALL_LIBDIR}")
elseif(UNIX AND NOT APPLE)
  set_target_properties(${NAME} PROPERTIES INSTALL_RPATH
                                           "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}")
endif()

target_include_directories(
  ${NAME}
  PUBLIC ${PROJECT_SOURCE_DIR}/src/cc/
         $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
         $<INSTALL_INTERFACE:include>)

target_link_libraries(${NAME} gtest ${PROJECT_NAME}::BiDirectionalCpp lemon)

add_test(NAME ${NAME} COMMAND $<TARGET_FILE:${NAME}>)
