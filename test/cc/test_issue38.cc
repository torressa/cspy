#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/utils.h"

namespace bidirectional {

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

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, 0, 2, max_res, min_res);
    // Create graph
    bidirectional->addNodes({0, 1, 2});
    bidirectional->addEdge(0, 1, 0.0, {1, 2});
    bidirectional->addEdge(1, 2, 0.0, {1, 10});
  }
};

TEST_F(TestIssue38, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}
} // namespace bidirectional
