#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"

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
};

void createGraphIssue69(BiDirectional* bidirectional) {
  bidirectional->addNodes({1, 3, 0, 6, 7});
  bidirectional->addEdge(1, 3, 3.0, {7, 13});
  bidirectional->addEdge(3, 0, 4.0, {8, 10});
  bidirectional->addEdge(3, 6, 7.0, {8, 3});
  bidirectional->addEdge(3, 7, 1.0, {15, 12});
  bidirectional->addEdge(0, 7, 7.0, {6, 3});
  bidirectional->addEdge(6, 7, 8.0, {3, 8});
}

TEST_F(TestIssue69, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  createGraphIssue69(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue69, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->setDirection("forward");
  createGraphIssue69(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue69, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->setDirection("backward");
  createGraphIssue69(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

} // namespace bidirectional
