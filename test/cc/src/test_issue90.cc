#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"

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
};

void createGraphIssue90(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2, 3, 4, 5});
  bidirectional->addEdge(0, 1, 1.0, {1, -1});
  bidirectional->addEdge(1, 2, 1.0, {1, 1});
  bidirectional->addEdge(3, 4, 1.0, {1, 1});
  bidirectional->addEdge(4, 5, 1.0, {1, 1});
}

TEST_F(TestIssue90, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  createGraphIssue90(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue90, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->setDirection("forward");
  createGraphIssue90(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue90, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->setDirection("backward");
  createGraphIssue90(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

} // namespace bidirectional
