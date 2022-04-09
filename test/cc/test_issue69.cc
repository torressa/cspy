#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/utils.h"

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

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, source_id, sink_id, max_res, min_res);
    // Create graph
    bidirectional->addNodes({1, 3, 0, 6, 7});
    bidirectional->addEdge(1, 3, 3.0, {7, 13});
    bidirectional->addEdge(3, 0, 4.0, {8, 10});
    bidirectional->addEdge(3, 6, 7.0, {8, 3});
    bidirectional->addEdge(3, 7, 1.0, {15, 12});
    bidirectional->addEdge(0, 7, 7.0, {6, 3});
    bidirectional->addEdge(6, 7, 8.0, {3, 8});
  }
};

TEST_F(TestIssue69, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue69, testForward) {
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue69, testBackward) {
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

} // namespace bidirectional
