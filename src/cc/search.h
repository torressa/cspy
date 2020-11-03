#ifndef BIDIRECTIONAL_SEARCH_H__
#define BIDIRECTIONAL_SEARCH_H__

#include <vector>

#include "digraph.h"
#include "labelling.h"
#include "py_ref_callback.h"

namespace bidirectional {

class Search {
 public:
  // ctor
  Search(
      const DiGraph*                   graph,
      const std::vector<double>&       max_res,
      const std::vector<double>&       min_res,
      const std::string&               direction,
      const bool&                      elementary,
      const int&                       dominance_frequency,
      const labelling::LabelExtension& label_extension,
      const bool&                      save);
  // dtor
  ~Search();

  // Inputs
  const DiGraph*            graph_ptr;
  const std::vector<double> max_res;
  const std::vector<double> min_res;
  const std::string         direction;
  const bool                elementary;
  const int                 dominance_frequency;

  // Algorithm members
  // stopping criteria / counts
  bool stop              = false;
  int  unprocessed_count = 0;
  int  processed_count   = 0;
  int  generated_count   = 0;
  // labels
  std::shared_ptr<labelling::Label> current_label;
  std::shared_ptr<labelling::Label> final_label;

  std::unique_ptr<std::vector<labelling::Label>> best_labels;
  // current resources
  std::vector<double> max_res_curr, min_res_curr;
  // Stopping criteria

  void move(std::vector<double> current_resource_bound);
  void call() const;
  void cleanUp();

 private:
  /// label extension class
  const labelling::LabelExtension label_extension_;
  /// Parameter to indicate whether lists of non_dominated labels should be
  /// kept. Only when the search is bidirectional.
  bool save_nondominated_ = true;
  /// iteration number
  int iteration_ = 0;
  /// heap vector to keep ordered set of unprocessed labels.
  /// the order depends on the on the direction of the search. i.e. forward ->
  /// increasing in the monotone resource, backward -> decreasing in the
  /// monotone resource.
  std::unique_ptr<std::vector<labelling::Label>> unprocessed_labels_;
  // Methods
  // initialisation
  void initResourceBounds();
  void initLabels();
  void initContainers();
  // search
  void runSearch();
  void updateCurrentLabel();
  void updateHalfWayPoints();
  void extendCurrentLabel();
  void saveCurrentBestLabel();
};
} // namespace bidirectional
#endif // BIDIRECTIONAL_SEARCH_H__
