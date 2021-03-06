#include "test_issue41.h"

#include <iostream>
#include <numeric>

namespace bidirectional {

void addEdgesIssue41(BiDirectional* bidirectional) {
  bidirectional->addEdge("Source", "A", 10.0, {1.0, 1.0});
  bidirectional->addEdge("A", "B", 3.0, {1.0, 0.0});
  bidirectional->addEdge("A", "C", 10.0, {1.0, 1.0});
  bidirectional->addEdge("B", "C", 3.0, {1.0, 0.0});
  bidirectional->addEdge("B", "Sink", 5.0, {1.0, 1.0});
  bidirectional->addEdge("C", "Sink", 0.0, {1.0, 1.0});
}

TEST_F(TestIssue41, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testBothElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.elementary = true;
  addEdgesIssue41(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testBothUnprocessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.method = "unprocessed";
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.method = "processed";
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.method = "generated";
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction = "forward";
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testForwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction  = "forward";
  bidirectional->options.elementary = true;
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction = "backward";
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue41, testBackwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);
  bidirectional->options.direction  = "backward";
  bidirectional->options.elementary = true;
  addEdgesIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

} // namespace bidirectional
