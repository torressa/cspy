#ifndef TEST_TEST_BIDIRECTIONAL_H__
#define TEST_TEST_BIDIRECTIONAL_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

class TestBiDirectional : public ::testing::Test {
 protected:
  std::unique_ptr<BiDirectional> bidirectional;
  const int                      number_vertices = 5;
  const int                      number_edges    = 5;
  const std::vector<double>      max_res         = {4.0, 20.0};
  const std::vector<double>      min_res         = {0.0, 0.0};
  const std::vector<int>         final_path      = {0, 1, 2, 3, 4};
  const std::vector<double>      final_res       = {4.0, 15.3};
  const double                   final_cost      = -13.0;
};

} // namespace bidirectional

#endif // TEST_TEST_BIDIRECTIONAL_H__
