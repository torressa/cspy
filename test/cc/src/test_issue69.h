#ifndef TEST_TEST_ISSUE69_H__
#define TEST_TEST_ISSUE69_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

class TestIssue69 : public ::testing::Test {
 protected:
  const int                      number_vertices = 5;
  const int                      number_edges    = 6;
  const int                      source_id       = 1;
  const int                      sink_id         = 7;
  const std::vector<double>      max_res         = {20.0, 30.0};
  const std::vector<double>      min_res         = {1.0, 0.0};
  std::unique_ptr<BiDirectional> bidirectional;
  // Expected non-elementary solution
  const std::vector<int>    final_path = {1, 3, 6, 7};
  const std::vector<double> final_res  = {18.0, 24.0};
  const double              final_cost = 18.0;
};

} // namespace bidirectional

#endif // TEST_TEST_ISSUE69_H__
