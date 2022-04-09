#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/utils.h"

namespace bidirectional {

class TestIssue90 : public ::testing::Test {
 protected:
  const int                      number_vertices = 6;
  const int                      number_edges    = 5;
  const int                      source_id       = 0;
  const int                      sink_id         = 5;
  const std::vector<double>      max_res         = {6.0, 100.0};
  const std::vector<double>      min_res         = {0.0, -100.0};
  std::unique_ptr<BiDirectional> bidirectional;
  // Expected non-elementary solution
  const std::vector<int>    final_path = {0, 1, 2, 3, 4, 5};
  const std::vector<double> final_res  = {5.0, 3.0};
  const double              final_cost = 5.0;

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, source_id, sink_id, max_res, min_res);
    // Create graph
    bidirectional->addNodes({0, 1, 2, 3, 4, 5});
    bidirectional->addEdge(0, 1, 1.0, {1, -1});
    bidirectional->addEdge(1, 2, 1.0, {1, 1});
    bidirectional->addEdge(2, 3, 1.0, {1, 1});
    bidirectional->addEdge(3, 4, 1.0, {1, 1});
    bidirectional->addEdge(4, 5, 1.0, {1, 1});
  }
};

TEST_F(TestIssue90, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue90, testForward) {
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue90, testBackward) {
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

} // namespace bidirectional
