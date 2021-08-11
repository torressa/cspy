#ifndef BIDIRECTIONAL_SEARCH_H__
#define BIDIRECTIONAL_SEARCH_H__

#include <memory> // unique_ptr
#include <set>
#include <vector>

#include "labelling.h"

namespace bidirectional {

class Search {
 public:
  /// Direction of Search
  Directions direction;
  //  Params     params;
  /// Stopping criteria for each direction
  bool stop = false;
  /// Stopping criteria for each direction
  bool bound_exceeded = false;
  /// Number of unprocessed labels generated
  int unprocessed_count = 0;
  /// Number of labels processed
  int processed_count = 0;
  /// Number of labels generated (includes the possibly infeasible extensions)
  int generated_count = 0;

  /* Search-related parameters */

  /// Lower bounds from any node to sink
  std::unique_ptr<std::vector<double>> lower_bound_weight;
  /// vector with indices of vertices visited
  std::set<int>                     visited_vertices;
  std::shared_ptr<labelling::Label> current_label;
  /// Intermediate current best label with possibly complete source-sink path
  /// (shared pointer as we want to be able to substitute it without
  /// resetting)
  std::shared_ptr<labelling::Label> intermediate_label;

  /// vector with pareto optimal labels (per node) in each direction
  std::vector<std::vector<labelling::Label>> efficient_labels;
  /// vector with pointer to label with least weight (per node) in each
  /// direction
  std::vector<std::shared_ptr<labelling::Label>> best_labels;
  /**
   * heap vector to keep unprocessed labels ordered.
   * the order depends on the on the direction of the search.
   * i.e. forward -> increasing in the monotone resource,
   * backward -> decreasing in the monotone resource.
   */
  std::unique_ptr<std::vector<labelling::Label>> unprocessed_labels;

  // TODO: Use bucket-heap
  /* Heap operations for vector of labels */

  /**
   * Initialises heap using the appropriate comparison
   * i.e. increasing in the monotone resource forward lists, decreasing
   * otherwise
   */
  void makeHeap();

  /**
   * Push new elements in heap using the appropriate comparison
   * i.e. increasing in the monotone resource forward lists, decreasing
   * otherwise
   */
  void pushHeap();

  void pushUnprocessedLabel(const labelling::Label& label) {
    unprocessed_labels->push_back(label);
    pushHeap();
  }

  void pushEfficientLabel(const int& lemon_id, const labelling::Label& label) {
    efficient_labels[lemon_id].push_back(label);
  }

  /// Replace best label
  void replaceBestLabel(const int& lemon_id, const labelling::Label& label) {
    auto label_ptr = std::make_shared<labelling::Label>(label);
    best_labels[lemon_id].swap(label_ptr);
  }

  /// Replace best label
  void replaceCurrentLabel(const labelling::Label& label) {
    auto label_ptr = std::make_shared<labelling::Label>(label);
    current_label.swap(label_ptr);
  }

  /// Replace intermediate label
  void replaceIntermediateLabel(const labelling::Label& label) {
    auto label_ptr = std::make_shared<labelling::Label>(label);
    intermediate_label.swap(label_ptr);
  }

  /// Update vertices visited
  void addVisitedVertex(const int& lemon_id) {
    visited_vertices.insert(lemon_id);
  }

  Search(const Directions& direction_in);
  ~Search(){};
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_SEARCH_H__
