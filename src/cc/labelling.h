#ifndef BIDIRECTIONAL_LABELLING_H__
#define BIDIRECTIONAL_LABELLING_H__

#include <cmath> // nan
#include <vector>

#include "digraph.h"
#include "ref_callback.h"

namespace labelling {

/**
 * Single node label. With resource, cost and other attributes.
 *
 * Main functionality includes:
 *   - Checking resource feasibility
 *   - Checking dominance
 */
class Label {
 public:
  double                weight               = 0.0;
  bidirectional::Vertex vertex               = {-1, -1};
  std::vector<double>   resource_consumption = {};
  std::vector<int>      partial_path         = {};
  std::vector<int>      unreachable_nodes    = {};
  // Phi value for joining algorithm from Righini and Salani (2006)
  double phi = std::nan("nan");

  /* Constructors */
  /// Dummy constructor
  Label(){};

  /// Constructor
  Label(
      const double&                weight_in,
      const bidirectional::Vertex& vertex_in,
      const std::vector<double>&   resource_consumption_in,
      const std::vector<int>&      partial_path_in,
      const bool&                  elementary_in = false);

  /// @overload with phi
  Label(
      const double&                weight_in,
      const bidirectional::Vertex& vertex_in,
      const std::vector<double>&   resource_consumption_in,
      const std::vector<int>&      partial_path_in,
      const double&                phi_in,
      const bool&                  elementary_in = false);

  /// default destructor
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

  /**
   * Check resource feasibility of current label i.e.
   * min_res[i] <= resource_consumption[i] <= max_res[i]
   * for i in 0..resource_consumption.size()
   *
   * @param[in] max_res, vector of double with upper bound(s) for resource
   * consumption
   * @param[in] min_res, vector of double with lower bound(s) for resource
   * consumption
   */
  bool checkFeasibility(
      const std::vector<double>& max_res,
      const std::vector<double>& min_res) const;

  /// Check if weight is under the input threshold.
  bool checkThreshold(const double& threshold) const;

  /// Check whether the current partial path is Source - Sink
  bool checkStPath(const int& source_id, const int& sink_id) const;
  /// set phi attribute for merged labels from Righini and Salani (2006)
  void setPhi(const double& phi_in) { phi = phi_in; }

  // operator overloads
  Label&               operator=(const Label& other) = default;
  friend bool          operator<(const Label& label1, const Label& label2);
  friend bool          operator>(const Label& label1, const Label& label2);
  friend std::ostream& operator<<(std::ostream& os, const Label& label);
  friend bool          operator==(const Label& label1, const Label& label2);
  friend bool          operator!=(const Label& label1, const Label& label2) {
    return !(label1 == label2);
  }
};

/**
 * Label extension using custom REFs if callback defined
 * Holds pointer to callback.
 * All calls to callback REF should be done through an instance of
 * `LabelExtension` as `label_extension.ref_callback->REF_fwd`
 */
class LabelExtension {
 public:
  LabelExtension(){};
  ~LabelExtension() {
    ref_callback = nullptr;
    delete ref_callback;
  };
  /// Callback to custom REF
  bidirectional::REFCallback* ref_callback = nullptr;

  /* Methods */
  /// Set callback for custom resource extensions
  void setREFCallback(bidirectional::REFCallback* cb);

  /**
   * Generate new label extensions from the current label and return only if
   * resource feasible.
   * The input label is a pointer as it may be modified in
   * the case that the edge / adjacent_vertex is found to be resource
   * infeasible, in which case, the head/tail node becomes unreachable and the
   * attribute is updated.
   *
   * @param[out] label, labelling::Label, current label to extend (and maybe
   * update `unreachable_nodes`)
   * @param[in] adjacent_vertex, AdjVertex, edge
   * @param[in] direction string
   * @param[in] elementary bool
   * @param[in] max_res, vector of double with upper bound(s) for resource
   * consumption
   * @param[in] min_res, vector of double with lower bound(s) for resource
   * consumption
   *
   * @return Label object with extended label. Note this may be empty if the
   * extension is resource infeasible
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
 * In the forward (backward) direction this is the label with lowest (highest)
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
 * Check whether the input label dominates any efficient label (previously
 * undominated labels) at the same node.
 * If any label is dominated by the input label, they are removed.
 *
 * @param[out] efficient_labels, pointer to a vector of Label with the efficient
 * labels at the same node as `label`. If a label is dominated by `label`, it is
 * removed from this vector.
 * @param[in] label, Label to compare
 * @param[in] direction, string with direction of search
 * @param[in] elementary, bool with whether non-elementary paths are allowed
 *
 * @return bool, true if `label` is dominated, false otherwise
 */
bool runDominanceEff(
    std::vector<Label>* efficient_labels_ptr,
    const Label&        label,
    const std::string&  direction,
    const bool&         elementary);

/**
 * Reverse backward path and inverts resource consumption
 * and returns resulting forward-compatible label.
 *
 * @param[out] label, labelling::Label, current label to extend (and maybe
 * update `unreachable_nodes`)
 * @param[in] max_res, vector of double with upper bound(s) for resource
 * consumption. To use to invert monotone resource
 * @param[in] invert_min_res, bool
 *
 * @return inverted label
 */
Label processBwdLabel(
    const labelling::Label&    label,
    const std::vector<double>& max_res,
    const std::vector<double>& cumulative_resource,
    const bool&                invert_min_res = false);

/**
 * Check whether a pair of forward and backward labels are suitable for merging.
 * To be used before attempting to merge.
 */
bool mergePreCheck(
    const labelling::Label&   fwd_label,
    const labelling::Label&   bwd_label,
    const std::vector<double> max_res,
    const bool&               elementary);

/**
 * Returns the phi value.
 * As defined in Righini and Salani (2006)
 */
double getPhiValue(
    const labelling::Label&    fwd_label,
    const labelling::Label&    bwd_label,
    const std::vector<double>& max_res);

/**
 * Check whether the pair (phi, path) is already contained in all the (phi,
 * path) pairs with a lower phi.
 *
 * As defined in Righini and Salani (2006)
 */
bool halfwayCheck(const Label& label, const std::vector<Label>& labels);

/**
 * Merge labels produced by a backward and forward label.
 * If an s-t compatible path can be obtained the appropriately
 * extended and merged label is returned.
 *
 * @return merged label with updated attributes and new phi value.
 */
Label mergeLabels(
    const labelling::Label&         fwd_label,
    const labelling::Label&         bwd_label,
    const LabelExtension&           label_extension_,
    const bidirectional::AdjVertex& adj_vertex,
    const bidirectional::Vertex&    sink,
    const std::vector<double>&      max_res,
    const std::vector<double>&      min_res);

// TODO: Use bucket-heap
/* Heap operations for vector of labels */

/**
 * Initialises heap using the appropriate comparison
 * i.e. increasing in the monotone resource forward lists, decreasing otherwise
 */
void makeHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction);

/**
 * Push new elements in heap using the appropriate comparison
 * i.e. increasing in the monotone resource forward lists, decreasing otherwise
 */
void pushHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction);

} // namespace labelling

#endif // BIDIRECTIONAL_LABELLING_H__
