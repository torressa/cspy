#include "test_bidirectional.h"

#include <iostream>
#include <numeric>

namespace bidirectional {

void addEdges(BiDirectional* bidirectional) {
  bidirectional->addEdge("Source", "A", -1, {1, 2});
  bidirectional->addEdge("A", "B", -1, {1, 0.3});
  bidirectional->addEdge("B", "C", -10, {1, 3});
  bidirectional->addEdge("B", "Sink", 10, {1, 2});
  bidirectional->addEdge("C", "Sink", -1, {1, 10});
}

TEST_F(TestBiDirectional, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();

  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestBiDirectional, testBothTimeLimit) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->time_limit = 0.05;
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestBiDirectional, testBothThreshold) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->threshold = 100;
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();

  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  std::vector<std::string> path_ = {"Source", "A", "B", "Sink"};
  std::vector<double>      res_  = {3.0, 4.3};
  double                   cost_ = 8;

  ASSERT_TRUE(path == path_);
  ASSERT_TRUE(res == res_);
  ASSERT_TRUE(cost == cost_);
}

// TODO fix method="random". See issues
// TEST_F(TestBiDirectional, testBothRandom) {
//   bidirectional = std::make_unique<BiDirectional>(
//       number_vertices, number_edges, max_res, min_res);
//   bidirectional->method = "random";
//   addEdges(bidirectional.get());
//   auto path = bidirectional->getPath();
//   ASSERT_TRUE(path.size() == 0);
//   bidirectional->run();
//   path      = bidirectional->getPath();
//   auto res  = bidirectional->getConsumedResources();
//   auto cost = bidirectional->getTotalCost();
//   ASSERT_TRUE(path == final_path);
//   ASSERT_TRUE(res == final_res);
//   ASSERT_TRUE(cost == final_cost);
// }

TEST_F(TestBiDirectional, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->method = "processed";
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();
  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestBiDirectional, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->method = "generated";
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();
  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestBiDirectional, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->direction = "forward";
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();
  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestBiDirectional, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->direction = "backward";
  addEdges(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);
  bidirectional->run();
  path = bidirectional->getPath();

  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();
  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

} // namespace bidirectional
