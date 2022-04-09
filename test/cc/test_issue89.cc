#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "test/cc/utils.h"

namespace bidirectional {

class TestIssue89 : public ::testing::Test {
 protected:
  const int                      number_vertices = 10;
  const int                      number_edges    = 25;
  const int                      source_id       = 9;
  const int                      sink_id         = 8;
  const std::vector<double>      max_res         = {10.0, 100, 0};
  const std::vector<double>      min_res         = {0.0, 1.0};
  std::unique_ptr<BiDirectional> bidirectional;
  // Expected non-elementary solution
  const std::vector<int>    final_path = {9, 0, 8};
  const std::vector<double> final_res  = {2.0, 1.0};
  const double              final_cost = 2.0;

  void SetUp() override {
    bidirectional = std::make_unique<BiDirectional>(
        number_vertices, number_edges, source_id, sink_id, max_res, min_res);

    bidirectional->addNodes({9, 0, 1, 2, 3, 4, 5, 6, 7, 8});
    std::vector<double> rc{1.0, 0.0};

    bidirectional->addEdge(0, 3, 1, rc);
    bidirectional->addEdge(0, 5, 1, rc);
    bidirectional->addEdge(0, 8, 1, rc);
    bidirectional->addEdge(1, 3, 1, rc);
    bidirectional->addEdge(1, 5, 1, rc);
    bidirectional->addEdge(1, 8, 1, rc);
    bidirectional->addEdge(2, 1, 1, rc);
    bidirectional->addEdge(2, 4, 1, rc);
    bidirectional->addEdge(2, 8, 1, rc);
    bidirectional->addEdge(3, 1, 1, rc);
    bidirectional->addEdge(3, 4, 1, rc);
    bidirectional->addEdge(3, 8, 1, rc);
    bidirectional->addEdge(4, 0, 1, rc);
    bidirectional->addEdge(4, 2, 1, rc);
    bidirectional->addEdge(4, 8, 1, rc);
    bidirectional->addEdge(5, 0, 1, rc);
    bidirectional->addEdge(5, 2, 1, rc);
    bidirectional->addEdge(5, 8, 1, rc);
    // Only resource feasible edge
    bidirectional->addEdge(9, 0, 1, {1, 1});
    bidirectional->addEdge(9, 1, 1, rc);
    bidirectional->addEdge(9, 2, 1, rc);
    bidirectional->addEdge(9, 3, 1, rc);
    bidirectional->addEdge(9, 4, 1, rc);
    bidirectional->addEdge(9, 5, 1, rc);
  }
};

TEST_F(TestIssue89, testBothElementary) {
  bidirectional->setElementary(true);
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue89, testForwardElementary) {
  bidirectional->setElementary(true);
  bidirectional->setDirection("forward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

TEST_F(TestIssue89, testBackwardElementary) {
  bidirectional->setElementary(true);
  bidirectional->setDirection("backward");
  bidirectional->run();
  checkResult(*bidirectional, final_path, final_res, final_cost);
}

} // namespace bidirectional
