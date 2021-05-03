#include "test_labelling.h"

#include <algorithm> // make_heap, push_heap
#include <memory>    // make_unique

namespace labelling {

TEST_F(TestLabelling, testDominance) {
  const Label         label(weight, node, res, path);
  std::vector<double> res2 = {6.0, -3.0};
  const Label         label2(weight, node, res2, path);
  const Label         label3(weight, node, res2, path);

  ASSERT_TRUE(label2.checkDominance(label, "forward", false));
  ASSERT_FALSE(label.checkDominance(label2, "forward", false));
  ASSERT_TRUE(label3.checkDominance(label, "forward", false));
  ASSERT_FALSE(label3.checkDominance(label2, "backward", false));
}

TEST_F(TestLabelling, testThreshold) {
  const Label  label(weight, node, res, path);
  const double threshold1 = 11.0;
  const double threshold2 = 0.0;

  ASSERT_TRUE(label.checkThreshold(threshold1));
  ASSERT_FALSE(label.checkThreshold(threshold2));
}

TEST_F(TestLabelling, testStPath) {
  const Label      label(weight, node, res, path);
  std::vector<int> path2 = {0, 10};
  const Label      label2(weight, node, res, path2);

  ASSERT_FALSE(label.checkStPath(0, 10));
  ASSERT_TRUE(label2.checkStPath(0, 10));
}

TEST_F(TestLabelling, testFeasibility) {
  const Label               label(weight, node, res, path);
  const std::vector<double> max_res = {10.0, 10.0};
  const std::vector<double> min_res = {0.0, 0.0};

  ASSERT_TRUE(label.checkFeasibility(max_res, min_res));
  ASSERT_FALSE(label.checkFeasibility(min_res, max_res));
}

TEST_F(TestLabelling, testExtendForward) {
  Label label(weight, node, res, path);
  auto  labels                         = std::make_unique<std::vector<Label>>();
  auto  label_extension                = std::make_unique<LabelExtension>();
  const bidirectional::AdjVertex adj_v = {other_node, weight, res};

  std::make_heap(labels->begin(), labels->end(), std::greater<>{});
  labels->push_back(label);
  Label new_label = label_extension->extend(
      &label, adj_v, "forward", false, max_res, min_res);
  labels->push_back(new_label);
  std::push_heap(labels->begin(), labels->end(), std::greater<>{});

  ASSERT_EQ(labels->size(), 2);
  // Should return labels in decreasing order of the monotone resource
  Label next_label = getNextLabel(labels.get(), "forward");
  ASSERT_EQ(labels->size(), 1);
  ASSERT_EQ(next_label.resource_consumption[0], 6);
  ASSERT_EQ(next_label.vertex.lemon_id, 1);
  Label last_label = getNextLabel(labels.get(), "forward");
  ASSERT_EQ(labels->size(), 0);
  ASSERT_EQ(last_label.resource_consumption[0], 12);
  ASSERT_EQ(last_label.vertex.lemon_id, 2);
}

TEST_F(TestLabelling, testExtendBackward) {
  Label label(weight, node, res, path);
  auto  labels          = std::make_unique<std::vector<Label>>();
  auto  label_extension = std::make_unique<LabelExtension>();

  const bidirectional::AdjVertex adj_v     = {other_node, weight, res};
  const std::string              direction = "backward";
  // Max-heap
  std::make_heap(labels->begin(), labels->end());
  // Insert current label
  labels->push_back(label);
  // extend current label
  Label new_label = label_extension->extend(
      &label, adj_v, direction, false, max_res, min_res);
  labels->push_back(new_label);
  std::push_heap(labels->begin(), labels->end());

  // Should return labels in increasing order of the monotone resource
  ASSERT_EQ(labels->size(), 2);
  Label next_label = getNextLabel(labels.get(), "backward");
  ASSERT_EQ(next_label.resource_consumption[0], 6);
  ASSERT_EQ(labels->size(), 1);
  Label last_label = getNextLabel(labels.get(), "backward");
  ASSERT_EQ(labels->size(), 0);
  ASSERT_EQ(last_label.resource_consumption[0], 0);
  ASSERT_EQ(last_label.vertex.lemon_id, 2);
}

TEST_F(TestLabelling, testRunDominanceForward) {
  std::vector<double> res2 = {3.0, -3.0};
  std::vector<double> res3 = {1.0, -3.0};
  const Label         label1(weight, node, res, path);
  const Label         label2(weight, node, res2, path);
  const Label         label3(weight, node, res3, path);

  auto labels = std::make_unique<std::vector<Label>>();

  std::make_heap(labels->begin(), labels->end(), std::greater<>{});

  // Insert labels
  labels->push_back(label1);
  labels->push_back(label2);
  std::push_heap(labels->begin(), labels->end(), std::greater<>{});

  ASSERT_EQ(labels->size(), 2);
  runDominanceEff(labels.get(), label3, "forward", false);
  ASSERT_EQ(labels->size(), 0);
}

TEST_F(TestLabelling, testRunDominanceBackward) {
  std::vector<double> res2 = {3.0, res[1]};
  std::vector<double> res3 = {7.0, res[1]};
  const Label         label1(weight, node, res, path);
  const Label         label2(weight, node, res2, path);
  const Label         label3(weight, node, res3, path);

  auto labels = std::make_unique<std::vector<Label>>();

  std::make_heap(labels->begin(), labels->end());
  labels->push_back(label1);
  labels->push_back(label2);
  std::push_heap(labels->begin(), labels->end());

  ASSERT_EQ(labels->size(), 2);
  runDominanceEff(labels.get(), label3, "backward", false);
  ASSERT_EQ(labels->size(), 0);
}

} // namespace labelling

// namespace labelling
