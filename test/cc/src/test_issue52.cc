#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/src/utils.h"

namespace bidirectional {

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

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, source_id, sink_id, max_res, min_res);
    // Create graph
    bidirectional->addNodes({0, 1, 2, 3, 4});
    bidirectional->addEdge(0, 1, 0.0, {1});
    bidirectional->addEdge(1, 2, -10.0, {1});
    bidirectional->addEdge(2, 3, -10.0, {1});
    bidirectional->addEdge(3, 1, -10.0, {1});
    bidirectional->addEdge(1, 4, 0.0, {1});
  }
};

TEST_F(TestIssue52, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue52, testBothElementary) {
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, elementary_path, elementary_res, elementary_cost);
}

TEST_F(TestIssue52, testBothUnprocessed) {
  bidirectional->setMethod("unprocessed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue52, testBothProcessed) {
  bidirectional->setMethod("processed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue52, testBothGenerated) {
  bidirectional->setMethod("generated");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue52, testForward) {
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue52, testForwardElementary) {
  bidirectional->setDirection("forward");
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, elementary_path, elementary_res, elementary_cost);
}

TEST_F(TestIssue52, testBackward) {
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue52, testBackwardElementary) {
  bidirectional->setDirection("backward");
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, elementary_path, elementary_res, elementary_cost);
}

} // namespace bidirectional
