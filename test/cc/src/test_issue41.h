#ifndef TEST_TEST_ISSUE41_H__
#define TEST_TEST_ISSUE41_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

class TestIssue41 : public ::testing::Test {
 protected:
  const int                      number_vertices = 5;
  const int                      number_edges    = 6;
  const std::vector<double>      max_res         = {3.0, 3.0};
  const std::vector<double>      min_res         = {0.0, 3.0};
  std::unique_ptr<BiDirectional> bidirectional;

  // expected solution
  const std::vector<int>    final_path = {0, 1, 3, 4};
  const std::vector<double> final_res  = {3.0, 3.0};
  const double              final_cost = 20.0;
};

} // namespace bidirectional

#endif // TEST_TEST_ISSUE41_H__
