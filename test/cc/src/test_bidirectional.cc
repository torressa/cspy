#include "test_bidirectional.h"

#include <numeric>

namespace bidirectional {

void createGraph(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2, 3, 4});
  // Add edges
  bidirectional->addEdge(0, 1, -1, {1, 2});
  bidirectional->addEdge(1, 2, -1, {1, 0.3});
  bidirectional->addEdge(2, 3, -10, {1, 3});
  bidirectional->addEdge(2, 4, 10, {1, 2});
  bidirectional->addEdge(3, 4, -1, {1, 10});
}

TEST_F(TestBiDirectional, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestBiDirectional, testBothTimeLimit) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.time_limit = 0.001;
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestBiDirectional, testBothThreshold) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.threshold = 100;
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  std::vector<int>    path_ = {0, 1, 2, 4};
  std::vector<double> res_  = {3.0, 4.3};
  double              cost_ = 8;

  ASSERT_EQ(path, path_);
  ASSERT_EQ(res, res_);
  ASSERT_EQ(cost, cost_);
}

TEST_F(TestBiDirectional, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.method = "processed";
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestBiDirectional, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.method = "generated";
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestBiDirectional, testBothBoundsPruning) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.bounds_pruning = true;
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestBiDirectional, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.direction = "forward";
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestBiDirectional, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.direction = "backward";
  createGraph(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

} // namespace bidirectional
