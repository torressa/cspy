# Use latest UseSWIG module
cmake_minimum_required(VERSION 3.14)

project(
  boost_r_c_shortest_paths
  VERSION 1.0.0
  LANGUAGES CXX)

find_package(Boost REQUIRED)

set(NAME run_r_c_shortest_paths)

add_executable(${NAME} r_c_shortest_paths.cc)

target_include_directories(
  ${NAME} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                 $<INSTALL_INTERFACE:include> ${Boost_INCLUDE_DIRS})
target_link_libraries(${NAME} ${Boost_LIBRARIES})
