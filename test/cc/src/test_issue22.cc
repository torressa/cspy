#include "test_issue22.h"

#include <numeric>

namespace bidirectional {

void createGraphIssue22(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2, 3, 4});
  bidirectional->addEdge(0, 1, 10, {1, 1});
  bidirectional->addEdge(0, 2, 10, {1, 1});
  bidirectional->addEdge(0, 3, 10, {1, 1});
  bidirectional->addEdge(1, 4, -10, {1, 0});
  bidirectional->addEdge(2, 4, -10, {1, 0});
  bidirectional->addEdge(3, 4, -10, {1, 0});
  bidirectional->addEdge(3, 2, -5, {1, 1});
  bidirectional->addEdge(2, 1, -10, {1, 1});
}

TEST_F(TestIssue22, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 4, max_res, min_res);
  createGraphIssue22(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

} // namespace bidirectional
