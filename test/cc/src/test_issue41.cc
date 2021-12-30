#include <iostream>
#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"

namespace bidirectional {

class TestIssue41 : public ::testing::Test {
 protected:
  const int                      number_vertices = 5;
  const int                      number_edges    = 6;
  const std::vector<double>      max_res         = {3.0, 3.0};
  const std::vector<double>      min_res         = {0.0, 3.0};
  std::unique_ptr<BiDirectional> bidirectional;

  // expected solution
  const std::vector<int>    final_path = {0, 1, 3, 4};
  const std::vector<double> final_res  = {3.0, 3.0};
  const double              final_cost = 20.0;
};

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

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testBothElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setElementary(true);
  createGraphIssue41(bidirectional.get());

  bidirectional->run();
  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testBothUnprocessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setMethod("unprocessed");
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testBothProcessed) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setMethod("processed");
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testBothGenerated) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setMethod("generated");
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testForward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setDirection("forward");
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testForwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setDirection("forward");
  bidirectional->setElementary(true);
  createGraphIssue41(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testBackward) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setDirection("backward");
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

TEST_F(TestIssue41, testBackwardElementary) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  bidirectional->setDirection("backward");
  bidirectional->setElementary(true);
  createGraphIssue41(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}

} // namespace bidirectional
