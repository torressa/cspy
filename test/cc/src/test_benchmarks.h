#ifndef TEST_TEST_BENCHMARKS_H__
#define TEST_TEST_BENCHMARKS_H__

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

/**
 * TestBenchmarks fixture class for unittests. Inherits from gtest.
 */
class TestBenchmarks : public ::testing::TestWithParam<int> {
 public:
  int               instance_number;
  const std::string path_to_data =
      "/root/benchmarks/beasley_christofides_1989/";
  const std::string              output_path = "/root/build/";
  std::unique_ptr<BiDirectional> bidirectional;
  double                         time_limit = 30;
  void SetUp() override { instance_number = GetParam(); }
};

} // namespace bidirectional

#endif // TEST_TEST_BENCHMARKS_H__
