#ifndef TEST_TEST_ISSUE17_H__
#define TEST_TEST_ISSUE17_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

void addEdgesIssue17(BiDirectional* bidirectional);

class TestIssue17 : public ::testing::Test {
 protected:
  const bool                     elementary      = true;
  const int                      number_vertices = 7;
  const int                      number_edges    = 11;
  const std::vector<double>      max_res         = {6.0, 6.0};
  const std::vector<double>      min_res         = {0.0, 0.0};
  std::unique_ptr<BiDirectional> bidirectional;
  const std::vector<int>         final_path = {0, 2, 5, 6};
  const std::vector<double>      final_res  = {3.0, 3.0};
  const double                   final_cost = 1.0;
};

} // namespace bidirectional

#endif // TEST_TEST_ISSUE17_H__
