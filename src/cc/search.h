#ifndef BIDIRECTIONAL_SEARCH_H__
#define BIDIRECTIONAL_SEARCH_H__

#include <cmath> // nan
#include <set>
#include <vector>

#include "digraph.h"
#include "labelling.h"

namespace bidirectional {

/**
 * Generic implementation for the search, can handle bakcward and forward
 * directions. It is worth noting that unprocessed labels are kept in a single
 * vector which is to be kept as a heap (make_heap at the start and push_heap
 * after insertions, @see labelling::makeHeap, labelling::pushHeap).
 * The reason here is for easier extraction of promising labels.
 * In the forward direction these are ones with smallest monotone resource
 * `resource_consumption[0]` i.e. unprocessed_labels_ is a min-heap.
 * In the backward direction, the opposite is true so max-heap.
 *
 * Efficient labels and others (`efficient_labels` and `best_labels`) are kept
 * in vectors indexed by node, again for easier extraction.
 */
class Search {
 public:
  Search(
      const DiGraph&                   graph,
      const std::vector<double>&       max_res,
      const std::vector<double>&       min_res,
      const std::string&               direction,
      const bool&                      elementary,
      const bool&                      bounds_pruning,
      const std::vector<double>&       lower_bound_weight,
      const labelling::LabelExtension& label_extension,
      const bool&                      direction_both);
  // dtor
  ~Search();

  // Inputs
  const DiGraph             graph;
  const std::vector<double> max_res;
  const std::vector<double> min_res;
  const std::string         direction;
  const bool                elementary;
  const bool                bounds_pruning;
  const std::vector<double> lower_bound_weight;

  // Algorithm members
  // stopping criteria / counts
  bool   stop              = false;
  int    unprocessed_count = 0;
  int    processed_count   = 0;
  int    generated_count   = 0;
  double primal_bound      = std::nan("nan");
  // labels
  std::shared_ptr<labelling::Label> current_label;
  std::shared_ptr<labelling::Label> final_label;

  /// vector with pareto optimal labels (per node)
  std::vector<std::vector<labelling::Label>> efficient_labels;
  /// vector with pointer to label with least weight (per node)
  std::vector<std::shared_ptr<labelling::Label>> best_labels;
  /// vector with indices of vertices visited
  std::set<int> visited_vertices;
  // current resources
  std::vector<double> max_res_curr, min_res_curr;
  /// advance the search updating the resource bounds from the opposite
  /// direction by a single step
  void move(const std::vector<double>& current_resource_bound);
  /// Set the primal bound
  void setPrimalBound(const double& new_primal_bound);
  /// Sorts efficient_labels for each vertex (not used as it takes too long)
  void cleanUp();
  /// checks if a given vertex has been visited
  /// @return true if it has been visited false otherwise
  bool checkVertexVisited(const int& vertex_idx) const;
  /// returns halfway point
  double getHalfWayPoint() const;

 private:
  /// label extension class
  const labelling::LabelExtension label_extension_;
  /// Boolean to indicate whether the algorithm is running in both directions or
  /// not
  bool direction_both_ = true;
  /// iteration number
  int iteration_ = 0;
  /// whether final_label contains a source-sink feasible path
  bool primal_st_bound_ = false;
  /// whether an external primal bound has been set
  bool   primal_bound_set_ = false;
  double primal_bound_     = std::nan("nan");
  /**
   * heap vector to keep unprocessed labels ordered.
   * the order depends on the on the direction of the search.
   * i.e. forward -> increasing in the monotone resource,
   * backward -> decreasing in the monotone resource.
   */
  std::unique_ptr<std::vector<labelling::Label>> unprocessed_labels_;

  // Methods
  // initialisation
  void initResourceBounds();
  /// Make `unprocessed_labels_` a heap for efficiency
  void initContainers();
  /// Construct first label and initialise `unprocessed_labels_` heap,
  /// `best_labels` source bucket and `visited_vertices`.
  void initLabels();
  // search
  void runSearch();
  /// Call labelling::getNextLabel to get next label in the heap
  /// (unprocessed_labels_) and update the current_label member
  void updateCurrentLabel();
  /// Update half-way points and check if the current labels violates them, in
  /// which case sets the stop member to true.
  void updateHalfWayPoints();
  /**
   * Given a candidate_label by looking at the vector of labels (bucket) for
   * that node, we can check if the candidate_label has already been saved or it
   * is dominated.
   * If both of these conditions are false, not seen and not
   * dominated, then we add it to the bucket.
   * Additionally, if the bounds_pruning option is active, we check the bounds
   * here, as an extra condition to add a label to the bucket.
   * Also, `visited_vertices` is updated here.
   */
  void updateEfficientLabels(const labelling::Label& candidate_label);
  /// Update `best_labels` entry by node with the current label if appropriate
  void updateBestLabels(const labelling::Label& candidate_label);
  /// Iterate over the neighbours for the current label node and save label
  /// extensions when appropriate. This is checked in updateEfficientLabels.
  void extendCurrentLabel();
  /// Save globally best label and check if it is Source-Sink so we can use it
  /// in the bounding. Sets `final_label`
  void saveCurrentBestLabel();
  /**
   * If bounds_pruning is true then check whether an input label plus a lower
   * bound for the path (from the node of the label to the source/sink) violates
   * the current primal bound.
   *
   * @return true if primal bound is violated, false otherwise.
   * i.e. if true, then input label cannot appear in the optimal solution.
   */
  bool checkPrimalBound(const labelling::Label& candidate_label) const;
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_SEARCH_H__
