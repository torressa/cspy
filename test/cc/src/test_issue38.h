#ifndef TEST_TEST_ISSUE38_H__
#define TEST_TEST_ISSUE38_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

void addEdgesIssue38(BiDirectional* bidirectional);

class TestIssue38 : public ::testing::Test {
 protected:
  const bool                     elementary      = true;
  const int                      number_vertices = 3;
  const int                      number_edges    = 2;
  const std::vector<double>      max_res         = {4.0, 20.0};
  const std::vector<double>      min_res         = {0.0, 0.0};
  std::unique_ptr<BiDirectional> bidirectional;
  const std::vector<int>         final_path = {0, 1, 2};
  const std::vector<double>      final_res  = {2.0, 12.0};
  const double                   final_cost = 0.0;
};

} // namespace bidirectional

#endif // TEST_TEST_ISSUE38_H__
