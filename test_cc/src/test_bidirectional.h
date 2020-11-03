#ifndef TEST_TEST_BIDIRECTIONAL_H__
#define TEST_TEST_BIDIRECTIONAL_H__

#include <memory>
#include <tuple>
#include <vector>

#include "bidirectional.h"
#include "gtest/gtest.h"

namespace bidirectional {

void addEdges(BiDirectional* bidirectional);

class TestBiDirectional : public ::testing::Test {
 protected:
  std::vector<double>            max_res = {4.0, 20.0};
  std::vector<double>            min_res = {0.0, 0.0};
  std::unique_ptr<BiDirectional> bidirectional;
  std::vector<std::string>       final_path = {"Source", "A", "B", "C", "Sink"};
  std::vector<double>            final_res  = {4.0, 15.3};
  double                         final_cost = -13.0;
};

} // namespace bidirectional

#endif // TEST_TEST_BIDIRECTIONAL_H__
