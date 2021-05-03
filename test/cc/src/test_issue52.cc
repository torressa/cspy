#include "test_issue52.h"

#include <iostream>
#include <numeric>

namespace bidirectional {

void createGraphIssue52(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2, 3, 4});
  bidirectional->addEdge(0, 1, 0.0, {1});
  bidirectional->addEdge(1, 2, -10.0, {1});
  bidirectional->addEdge(2, 3, -10.0, {1});
  bidirectional->addEdge(3, 1, -10.0, {1});
  bidirectional->addEdge(1, 4, 0.0, {1});
}

TEST_F(TestIssue52, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  createGraphIssue52(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue52, testBothElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.elementary = true;
  createGraphIssue52(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == elementary_path);
  ASSERT_TRUE(res == elementary_res);
  ASSERT_TRUE(cost == elementary_cost);
}

TEST_F(TestIssue52, testBothUnprocessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.method = "unprocessed";
  createGraphIssue52(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue52, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.method = "processed";
  createGraphIssue52(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue52, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.method = "generated";
  createGraphIssue52(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue52, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.direction = "forward";
  createGraphIssue52(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue52, testForwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.direction  = "forward";
  bidirectional->options.elementary = true;
  createGraphIssue52(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == elementary_path);
  ASSERT_TRUE(res == elementary_res);
  ASSERT_TRUE(cost == elementary_cost);
}

TEST_F(TestIssue52, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.direction = "backward";
  createGraphIssue52(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

TEST_F(TestIssue52, testBackwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, source_id, sink_id, max_res, min_res);
  bidirectional->options.direction  = "backward";
  bidirectional->options.elementary = true;
  createGraphIssue52(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == elementary_path);
  ASSERT_TRUE(res == elementary_res);
  ASSERT_TRUE(cost == elementary_cost);
}

} // namespace bidirectional
