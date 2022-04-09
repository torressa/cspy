#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/utils.h"

namespace bidirectional {

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

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, 0, 6, max_res, min_res);
    // Create graph
    bidirectional->addNodes({0, 1, 2, 3, 4, 5, 6});
    bidirectional->addEdge(0, 1, 3, {1, 1});
    bidirectional->addEdge(0, 2, 0, {1, 1});
    bidirectional->addEdge(1, 2, -1, {1, 1});
    bidirectional->addEdge(1, 4, 5, {1, 1});
    bidirectional->addEdge(2, 3, 3, {1, 1});
    bidirectional->addEdge(3, 1, 1, {1, 1});
    bidirectional->addEdge(2, 5, -1, {1, 1});
    bidirectional->addEdge(5, 6, 2, {1, 1});
    bidirectional->addEdge(5, 4, -1, {1, 1});
    bidirectional->addEdge(4, 2, 3, {1, 1});
    bidirectional->addEdge(4, 6, 3, {1, 1});
  }
};

TEST_F(TestIssue17, testBoth) {
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testBothElementary) {
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testBothUnprocessed) {
  bidirectional->setMethod("unprocessed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testBothProcessed) {
  bidirectional->setMethod("processed");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testBothGenerated) {
  bidirectional->setMethod("generated");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testForward) {
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testForwardElementary) {
  bidirectional->setDirection("forward");
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testBackward) {
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue17, testBackwardElementary) {
  bidirectional->setDirection("backward");
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

} // namespace bidirectional
