if(BUILD_PYTHON)
  return()
endif()

set(NAME BiDirectional_test)

if(BENCHMARK_TESTS)
  if(BENCHMARK_BOOST)
    find_package(Boost REQUIRED)
    add_executable(${NAME} main.cc test_benchmarks_boost.cc test_benchmarks.cc
                           utils.cc)
    target_include_directories(
      ${NAME}
      PUBLIC ${PROJECT_SOURCE_DIR}/src/cc/
             $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
             $<INSTALL_INTERFACE:include> ${Boost_INCLUDE_DIRS})
    target_link_libraries(${NAME} ${Boost_LIBRARIES} gtest
                          ${PROJECT_NAME}::BiDirectionalCpp)
  else()
    add_executable(${NAME} main.cc test_benchmarks.cc utils.cc)
  endif()
else()
  # Unit tests
  add_executable(
    ${NAME}
    main.cc
    utils.cc
    test_labelling.cc
    test_bidirectional.cc
    test_issue17.cc
    test_issue22.cc
    test_issue38.cc
    test_issue41.cc
    test_issue52.cc
    test_issue69.cc
    test_issue89.cc
    test_issue90.cc
    test_issue94.cc)
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
