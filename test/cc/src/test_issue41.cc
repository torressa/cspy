#include "test_issue41.h"

#include <iostream>
#include <numeric>

namespace bidirectional {

void createGraphIssue41(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2, 3, 4});
  bidirectional->addEdge(0, 1, 10.0, {1.0, 1.0});
  bidirectional->addEdge(1, 2, 3.0, {1.0, 0.0});
  bidirectional->addEdge(1, 3, 10.0, {1.0, 1.0});
  bidirectional->addEdge(2, 3, 3.0, {1.0, 0.0});
  bidirectional->addEdge(2, 4, 5.0, {1.0, 1.0});
  bidirectional->addEdge(3, 4, 0.0, {1.0, 1.0});
}

TEST_F(TestIssue41, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.elementary = true;
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.method = "unprocessed";
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.method = "processed";
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.method = "generated";
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.direction = "forward";
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.direction  = "forward";
  bidirectional->options.elementary = true;
  createGraphIssue41(bidirectional.get());
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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.direction = "backward";
  createGraphIssue41(bidirectional.get());

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
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->options.direction  = "backward";
  bidirectional->options.elementary = true;
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

} // namespace bidirectional
