#ifndef TEST_TEST_ISSUE52_H__
#define TEST_TEST_ISSUE52_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

void addEdgesIssue52(BiDirectional* bidirectional);

class TestIssue52 : public ::testing::Test {
 protected:
  const int                      number_vertices = 5;
  const int                      number_edges    = 5;
  const int                      source_id       = 0;
  const int                      sink_id         = 4;
  const std::vector<double>      max_res         = {5.0};
  const std::vector<double>      min_res         = {0.0};
  std::unique_ptr<BiDirectional> bidirectional;
  // Expected non-elementary solution
  const std::vector<int>    final_path = {0, 1, 2, 3, 1, 4};
  const std::vector<double> final_res  = {5.0};
  const double              final_cost = -30.0;
  // Expected Elementary solution
  const std::vector<int>    elementary_path = {0, 1, 4};
  const std::vector<double> elementary_res  = {2.0};
  const double              elementary_cost = 0.0;
};

} // namespace bidirectional

#endif // TEST_TEST_ISSUE52_H__
