#include "test_issue17.h"

#include <iostream>
#include <numeric>

namespace bidirectional {

void addEdgesIssue17(BiDirectional* bidirectional) {
  bidirectional->addEdge("Source", "1", 3, {1, 1});
  bidirectional->addEdge("Source", "2", 0, {1, 1});
  bidirectional->addEdge("1", "2", -1, {1, 1});
  bidirectional->addEdge("1", "4", 5, {1, 1});
  bidirectional->addEdge("2", "3", 3, {1, 1});
  bidirectional->addEdge("3", "1", 1, {1, 1});
  bidirectional->addEdge("2", "5", -1, {1, 1});
  bidirectional->addEdge("5", "Sink", 2, {1, 1});
  bidirectional->addEdge("5", "4", -1, {1, 1});
  bidirectional->addEdge("4", "2", 3, {1, 1});
  bidirectional->addEdge("4", "Sink", 3, {1, 1});
}

TEST_F(TestIssue17, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);

  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testBothElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->elementary = true;
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testBothUnprocessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->method = "unprocessed";
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->method = "processed";
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->method = "generated";
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->direction = "forward";
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testForwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->direction  = "forward";
  bidirectional->elementary = true;
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->direction = "backward";
  addEdgesIssue17(bidirectional.get());
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

TEST_F(TestIssue17, testBackwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->direction  = "backward";
  bidirectional->elementary = true;
  addEdgesIssue17(bidirectional.get());
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

} // namespace bidirectional
