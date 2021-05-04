#include "test_issue17.h"

#include <numeric>

namespace bidirectional {

void createGraphIssue17(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2, 3, 4, 5, 6});
  bidirectional->addEdge(0, 1, 3, {1, 1});
  bidirectional->addEdge(0, 2, 0, {1, 1});
  bidirectional->addEdge(1, 2, -1, {1, 1});
  bidirectional->addEdge(1, 4, 5, {1, 1});
  bidirectional->addEdge(2, 3, 3, {1, 1});
  bidirectional->addEdge(3, 1, 1, {1, 1});
  bidirectional->addEdge(2, 5, -1, {1, 1});
  bidirectional->addEdge(5, 6, 2, {1, 1});
  bidirectional->addEdge(5, 4, -1, {1, 1});
  bidirectional->addEdge(4, 2, 3, {1, 1});
  bidirectional->addEdge(4, 6, 3, {1, 1});
}

TEST_F(TestIssue17, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testBothElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.elementary = true;
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testBothUnprocessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.method = "unprocessed";
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.method = "processed";
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.method = "generated";
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.direction = "forward";
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testForwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.direction  = "forward";
  bidirectional->options.elementary = true;
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.direction = "backward";
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue17, testBackwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 6, max_res, min_res);
  bidirectional->options.direction  = "backward";
  bidirectional->options.elementary = true;
  createGraphIssue17(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

} // namespace bidirectional
