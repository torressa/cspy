#ifndef TEST_TEST_BENCHMARKS_BOOST_H__
#define TEST_TEST_BENCHMARKS_BOOST_H__

#include "gtest/gtest.h"

namespace boost {

/**
 * TestBenchmarks fixture class for unittests. Inherits from gtest.
 */
class TestBenchmarksBoost : public ::testing::TestWithParam<int> {
 public:
  int               instance_number;
  const std::string path_to_data =
      "/root/benchmarks/beasley_christofides_1989/";
  void SetUp() override { instance_number = GetParam(); }
};

} // namespace boost

#endif // TEST_TEST_BENCHMARKS_BOOST_H__
