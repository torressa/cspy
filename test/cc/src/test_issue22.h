#ifndef TEST_TEST_ISSUE22_H__
#define TEST_TEST_ISSUE22_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

void addEdgesIssue22(BiDirectional* bidirectional);

class TestIssue22 : public ::testing::Test {
 protected:
  const bool                     elementary      = true;
  const int                      number_vertices = 5;
  const int                      number_edges    = 8;
  const std::vector<double>      max_res         = {8.0, 2.0};
  const std::vector<double>      min_res         = {0.0, 0.0};
  std::unique_ptr<BiDirectional> bidirectional;
  const std::vector<std::string> final_path = {"Source", "2", "1", "Sink"};
  const std::vector<double>      final_res  = {3.0, 2.0};
  const double                   final_cost = -10.0;
};

} // namespace bidirectional

#endif // TEST_TEST_ISSUE22_H__
