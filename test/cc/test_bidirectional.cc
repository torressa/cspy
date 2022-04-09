#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
// cspy
#include "src/cc/bidirectional.h"
#include "test/cc/utils.h"

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

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, 0, 4, max_res, min_res);
    // Create graph
    bidirectional->addNodes({0, 1, 2, 3, 4});
    // Add edges
    bidirectional->addEdge(0, 1, -1, {1, 2});
    bidirectional->addEdge(1, 2, -1, {1, 0.3});
    bidirectional->addEdge(2, 3, -10, {1, 3});
    bidirectional->addEdge(2, 4, 10, {1, 2});
    bidirectional->addEdge(3, 4, -1, {1, 10});
  }
};

TEST_F(TestBiDirectional, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestBiDirectional, testBothTimeLimit) {
  bidirectional->setTimeLimit(0.001);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestBiDirectional, testBothThreshold) {
  bidirectional->setThreshold(100);
  bidirectional->run();

  std::vector<int>    path_ = {0, 1, 2, 4};
  std::vector<double> res_  = {3.0, 4.3};
  double              cost_ = 8;

  checkResult(*bidirectional, path_, res_, cost_);
}

TEST_F(TestBiDirectional, testBothProcessed) {
  bidirectional->setMethod("processed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestBiDirectional, testBothGenerated) {
  bidirectional->setMethod("generated");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestBiDirectional, testBothBoundsPruning) {
  bidirectional->setBoundsPruning(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestBiDirectional, testForward) {
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestBiDirectional, testBackward) {
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

} // namespace bidirectional
