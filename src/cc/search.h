#ifndef BIDIRECTIONAL_SEARCH_H__
#define BIDIRECTIONAL_SEARCH_H__

#include <cmath>
#include <vector>

#include "digraph.h"
#include "labelling.h"

namespace bidirectional {

class Search {
 public:
  // ctor
  Search(
      const DiGraph&                   graph,
      const std::vector<double>&       max_res,
      const std::vector<double>&       min_res,
      const std::string&               direction,
      const bool&                      elementary,
      const int&                       dominance_frequency,
      const std::vector<double>&       lower_bound_weight,
      const labelling::LabelExtension& label_extension,
      const bool&                      save);
  // dtor
  ~Search();

  // Inputs
  const DiGraph             graph;
  const std::vector<double> max_res;
  const std::vector<double> min_res;
  const std::string         direction;
  const bool                elementary;
  const int                 dominance_frequency;
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
  std::vector<int> visited_vertices;
  // current resources
  std::vector<double> max_res_curr, min_res_curr;
  /// advance the search updating the resource bounds from the opposite
  /// direction
  void move(const std::vector<double>& current_resource_bound);
  /// Sorts efficient_labels for each vertex
  void cleanUp();
  /// checks if a given vertex has been visited
  /// @return true if it has been visited false otherwise
  bool checkVertexVisited(const int& vertex_idx) const;
  /// returns halfway point
  double getHalfWayPoint() const;

 private:
  /// label extension class
  const labelling::LabelExtension label_extension_;
  /// Parameter to indicate whether lists of non_dominated labels should be
  /// kept. Only when the search is bidirectional.
  bool save_nondominated_ = true;
  /// iteration number
  int iteration_ = 0;
  /// whether dominance will be ran
  bool run_dominance_ = false;
  /// whether final_label contains a source-sink feasible path
  bool primal_st_bound_ = false;
  /**
   * heap vector to keep unprocessed labels ordered.
   * the order depends on the on the direction of the search. i.e. forward ->
   * increasing in the monotone resource, backward -> decreasing in the monotone
   * resource.
   */
  std::unique_ptr<std::vector<labelling::Label>> unprocessed_labels_;

  // Methods
  // initialisation
  void initResourceBounds();
  void initLabels();
  void initContainers();
  // search
  void runSearch();
  void updateCurrentLabel();
  /// update the efficient_labels given a candidate_label and a node index
  void updateEfficientLabels(
      const int&              vertex_idx,
      const labelling::Label& candidate_label);
  void updateBestLabels(
      const int&              vertex_idx,
      const labelling::Label& candidate_label);
  void updateHalfWayPoints();
  void extendCurrentLabel();
  void saveCurrentBestLabel();
  /**
   * check whether an input label violates the current primal bound.
   * @return true if primal bound is violated, false otherwise.
   * i.e. if true, then input label cannot appear in the optimal solution.
   */
  bool checkPrimalBound(const labelling::Label& candidate_label) const;
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_SEARCH_H__
