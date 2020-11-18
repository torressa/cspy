#include "test_issue22.h"

#include <numeric>

namespace bidirectional {

void addEdgesIssue22(BiDirectional* bidirectional) {
  bidirectional->addEdge("Source", "1", 10, {1, 1});
  bidirectional->addEdge("Source", "2", 10, {1, 1});
  bidirectional->addEdge("Source", "3", 10, {1, 1});
  bidirectional->addEdge("1", "Sink", -10, {1, 0});
  bidirectional->addEdge("2", "Sink", -10, {1, 0});
  bidirectional->addEdge("3", "Sink", -10, {1, 0});
  bidirectional->addEdge("3", "2", -5, {1, 1});
  bidirectional->addEdge("2", "1", -10, {1, 1});
}

TEST_F(TestIssue22, testBoth) {
  bidirectional = std::make_unique<BiDirectional>(
      number_vertices, number_edges, max_res, min_res);

  addEdgesIssue22(bidirectional.get());
  bidirectional->run();

  auto path = bidirectional->getPath();
  auto res  = bidirectional->getConsumedResources();
  auto cost = bidirectional->getTotalCost();

  ASSERT_TRUE(path == final_path);
  ASSERT_TRUE(res == final_res);
  ASSERT_TRUE(cost == final_cost);
}

} // namespace bidirectional
