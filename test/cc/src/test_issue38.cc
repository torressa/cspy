#include "test_issue38.h"

#include <numeric>

namespace bidirectional {

void addEdgesIssue38(BiDirectional* bidirectional) {
  bidirectional->addEdge("Source", "A", 0, {1, 2});
  bidirectional->addEdge("A", "Sink", 0, {1, 10});
}

TEST_F(TestIssue38, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);

  addEdgesIssue38(bidirectional.get());

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
