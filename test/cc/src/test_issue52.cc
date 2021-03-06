#include "test_issue52.h"

#include <iostream>
#include <numeric>

namespace bidirectional {

void addEdgesIssue52(BiDirectional* bidirectional) {
  bidirectional->addEdge("Source", "A", 0.0, {1});
  bidirectional->addEdge("A", "B", -10.0, {1});
  bidirectional->addEdge("B", "C", -10.0, {1});
  bidirectional->addEdge("C", "A", -10.0, {1});
  bidirectional->addEdge("A", "Sink", 0.0, {1});
}

TEST_F(TestIssue52, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  addEdgesIssue52(bidirectional.get());
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

TEST_F(TestIssue52, testBothElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.elementary = true;
  addEdgesIssue52(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);

  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == elementary_path);
  ASSERT_TRUE(res == elementary_res);
  ASSERT_TRUE(cost == elementary_cost);
}

TEST_F(TestIssue52, testBothUnprocessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.method = "unprocessed";
  addEdgesIssue52(bidirectional.get());
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

TEST_F(TestIssue52, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.method = "processed";
  addEdgesIssue52(bidirectional.get());
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

TEST_F(TestIssue52, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.method = "generated";
  addEdgesIssue52(bidirectional.get());
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

TEST_F(TestIssue52, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction = "forward";
  addEdgesIssue52(bidirectional.get());
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

TEST_F(TestIssue52, testForwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction  = "forward";
  bidirectional->options.elementary = true;
  addEdgesIssue52(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);

  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == elementary_path);
  ASSERT_TRUE(res == elementary_res);
  ASSERT_TRUE(cost == elementary_cost);
}

TEST_F(TestIssue52, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction = "backward";
  addEdgesIssue52(bidirectional.get());
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

TEST_F(TestIssue52, testBackwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction  = "backward";
  bidirectional->options.elementary = true;
  addEdgesIssue52(bidirectional.get());
  auto path = bidirectional->getPath();
  ASSERT_TRUE(path.size() == 0);

  bidirectional->run();
  path      = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == elementary_path);
  ASSERT_TRUE(res == elementary_res);
  ASSERT_TRUE(cost == elementary_cost);
}

} // namespace bidirectional
