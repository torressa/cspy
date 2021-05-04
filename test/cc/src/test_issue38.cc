#include "test_issue38.h"

#include <numeric>

namespace bidirectional {

void createGraphIssue38(BiDirectional* bidirectional) {
  bidirectional->addNodes({0, 1, 2});
  bidirectional->addEdge(0, 1, 0.0, {1, 2});
  bidirectional->addEdge(1, 2, 0.0, {1, 10});
}

TEST_F(TestIssue38, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, 0, 2, max_res, min_res);
  createGraphIssue38(bidirectional.get());

  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_EQ(path, final_path);
  ASSERT_EQ(res, final_res);
  ASSERT_EQ(cost, final_cost);
}
} // namespace bidirectional
