#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/src/utils.h"

namespace bidirectional {

class TestIssue41 : public ::testing::Test {
 protected:
  const int                      number_vertices = 5;
  const int                      number_edges    = 6;
  const std::vector<double>      max_res         = {3.0, 3.0};
  const std::vector<double>      min_res         = {0.0, 3.0};
  std::unique_ptr<BiDirectional> bidirectional;

  // expected solution
  const std::vector<int>    final_path = {0, 1, 3, 4};
  const std::vector<double> final_res  = {3.0, 3.0};
  const double              final_cost = 20.0;

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, 0, 4, max_res, min_res);
    // Create graph
    bidirectional->addNodes({0, 1, 2, 3, 4});
    bidirectional->addEdge(0, 1, 10.0, {1.0, 1.0});
    bidirectional->addEdge(1, 2, 3.0, {1.0, 0.0});
    bidirectional->addEdge(1, 3, 10.0, {1.0, 1.0});
    bidirectional->addEdge(2, 3, 3.0, {1.0, 0.0});
    bidirectional->addEdge(2, 4, 5.0, {1.0, 1.0});
    bidirectional->addEdge(3, 4, 0.0, {1.0, 1.0});
  }
};

TEST_F(TestIssue41, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testBothElementary) {
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testBothUnprocessed) {
  bidirectional->setMethod("unprocessed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testBothProcessed) {
  bidirectional->setMethod("processed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testBothGenerated) {
  bidirectional->setMethod("generated");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testForward) {
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testForwardElementary) {
  bidirectional->setDirection("forward");
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testBackward) {
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue41, testBackwardElementary) {
  bidirectional->setDirection("backward");
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

} // namespace bidirectional
