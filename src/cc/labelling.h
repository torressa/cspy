#ifndef BIDIRECTIONAL_LABELLING_H__
#define BIDIRECTIONAL_LABELLING_H__

#include <memory>
#include <vector>

#include "digraph.h"
#include "py_ref_callback.h"

namespace labelling {

/**
 * Single node label. With resource, cost and other attributes.
 * Note: Once created cannot be modified.
 *
 * Main functionality includes:
 *   - Checking resource feasibility
 *   - Cheking dominance
 */
class Label {
 public:
  double                   weight               = 0.0;
  bidirectional::Vertex    vertex               = {"", -1};
  std::vector<double>      resource_consumption = {};
  std::vector<std::string> partial_path         = {};
  std::vector<std::string> unreachable_nodes    = {};

  // constructors
  Label(){};
  Label(
      const double&                   weight,
      const bidirectional::Vertex&    vertex,
      const std::vector<double>&      resource_consumption,
      const std::vector<std::string>& partial_path,
      const bool&                     elementary = false);
  // default destructor
  ~Label(){};

  /**
   * Check if this dominates other.
   * Assumes the labels are comparable i.e. same nodes
   *
   * @param[in] other Label
   * @param[in] direction string
   * @param[in] elementary bool, optional
   * @return bool
   */
  bool checkDominance(
      const Label&       other,
      const std::string& direction,
      const bool&        elementary = false) const;
  /**
   * Checks whether `this` dominates `other` for the input direction. In the
   * case when neither dominates , i.e. they are non-dominated, the direction is
   * flipped labels are compared again.
   *
   * @param[in] other Label
   * @param[in] direction string
   * @param[in] elementary bool
   * @return bool
   */
  bool fullDominance(
      const Label&       other,
      const std::string& direction,
      const bool&        elementary) const;
  /// Check resource feasibility of current label
  bool checkFeasibility(
      const std::vector<double>& max_res,
      const std::vector<double>& min_res) const;
  /// Check if weight is under the input threshold.
  bool checkThreshold(const double& threshold) const;
  /// Check whether the current partial path is Source - Sink
  bool checkStPath() const;

  // opeator overloads
  Label&      operator=(const Label& other) = default;
  friend bool operator<(const Label& label1, const Label& label2);
  friend bool operator>(const Label& label1, const Label& label2) {
    return !(label1 < label2);
  }
  friend std::ostream& operator<<(std::ostream& os, const Label& label);
  friend bool          operator==(const Label& label1, const Label& label2);
  friend bool          operator!=(const Label& label1, const Label& label2) {
    return !(label1 == label2);
  }
};

/**
 * Label extention
 */
class LabelExtension {
 public:
  LabelExtension();
  ~LabelExtension();
  /// Python callback to custom REF
  bidirectional::PyREFCallback* py_callback = nullptr;
  /// Set python callback for custom resource extensions
  void setPyCallback(bidirectional::PyREFCallback* cb);
  /**
   * Generate new label extentions from the current label and return if resource
   * feasible.
   * The input label is a pointer as it may be modified in the case
   * that the edge / adjacent_vertex is found to be resource infeasible, in
   * which case, the head node becomes unreachable and the attribute is updated.
   *
   * @param[out] label, labelling::Label, current label to extend (and maybe
   * update `unreachable_nodes`)
   * @param[in] adjacent_vertex, AdjVertex, edge
   */
  Label extend(
      Label*                          label,
      const bidirectional::AdjVertex& adjacent_vertex,
      const std::string&              direction,
      const bool&                     elementary,
      const std::vector<double>&      max_res = {},
      const std::vector<double>&      min_res = {}) const;
};

/**
 * Get next label from ordered labels
 * Grabs the next element in the heap (back) and removes it
 * In the forward (backward) direction this is the label with least (most)
 * monotone resource.
 *
 * @param[out] labels, std::vector<Label> pointer (heap)
 * @param[in] direction, string
 */
Label getNextLabel(std::vector<Label>* labels, const std::string& direction);

/// Update efficient_labels using a candidate_label
void updateEfficientLabels(
    std::vector<Label>* efficient_labels,
    const Label&        candidate_label,
    const std::string&  direction,
    const bool&         elementary);

/**
 * Run dominance checks over all pairs of labels in `labels`
 * If `save` is true, the nondominated labels are added to `best_labels`.
 *
 * @param[out] labels, std::vector<Label> pointer
 * @param[in] direction, string with direction of search
 * @param[in] elementary, bool with whether non-elementary paths are allowed
 *
 * @return bool with true if either labels or best_labels have been updated,
 * false otherwise.
 */
bool runDominance(
    std::vector<Label>*                    labels,
    const std::string&                     direction,
    const bool&                            elementary,
    const std::vector<std::vector<Label>>& efficient_labels = {{}});

/// Run dominance for efficient_labels
bool runDominanceEff(
    std::vector<Label>* efficient_labels_ptr,
    const Label&        label,
    const std::string&  direction,
    const bool&         elementary);

/// Reverse backward path and inverts resource consumption
Label processBwdLabel(
    const labelling::Label&    label,
    const std::vector<double>& max_res,
    const std::vector<double>& cumulative_resource,
    const bool&                invert_min_res = false);
/**
 * Check whether a pair of forward and backward labels are suitable for merging.
 * To be used before attempting to merge
 */
bool mergePreCheck(
    const labelling::Label&   fwd_label,
    const labelling::Label&   bwd_label,
    const std::vector<double> max_res,
    const bool&               elementary);

/**
 * Merge labels produced by a backward and forward label.
 * If an s-t compatible path can be obtained the appropriately
 * extended and merged label is returned
 */
Label mergeLabels(
    const labelling::Label&       fwd_label,
    const labelling::Label&       bwd_label,
    const LabelExtension&         label_extension_,
    const bidirectional::DiGraph& graph,
    const std::vector<double>&    max_res,
    const std::vector<double>&    min_res);

// Heap operations for vector of Labels
/// Initalise heap using the appropriate comparison
/// i.e. increasing in the monotone resource forward lists, decreasing otherwise
void makeHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction);

/// Push new elements in heap using the appropriate comparison
/// i.e. increasing in the monotone resource forward lists, decreasing otherwise
void pushHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction);

} // namespace labelling

#endif // BIDIRECTIONAL_LABELLING_H__