#include "search.h"

#include <algorithm>
#include <iostream>
#include <set>

namespace bidirectional {

// ctor
Search::Search(
    const DiGraph*                   graph,
    const std::vector<double>&       max_res,
    const std::vector<double>&       min_res,
    const std::string&               direction,
    const bool&                      elementary,
    const int&                       dominance_frequency,
    const labelling::LabelExtension& label_extension,
    const bool&                      save_nondominated)
    : graph_ptr(graph),
      max_res(max_res),
      min_res(min_res),
      label_extension_(label_extension),
      direction(direction),
      elementary(elementary),
      dominance_frequency(dominance_frequency),
      save_nondominated_(save_nondominated) {
  unprocessed_labels_ = std::make_unique<std::vector<labelling::Label>>();
  best_labels         = std::make_unique<std::vector<labelling::Label>>();
  // Initalise resource bounds
  initResourceBounds();
  initLabels();
  initContainers();
}

// Default dtor
Search::~Search(){};

void Search::move(std::vector<double> current_resource_bound) {
  // Update current resources
  if (direction == "forward") {
    max_res_curr = current_resource_bound;
  } else {
    min_res_curr = current_resource_bound;
  }
  // Run
  if (unprocessed_labels_->size() > 0 || iteration_ == 0) {
    runSearch();
  } else {
    stop = true;
  }
}

void Search::call() const {
  if (label_extension_.py_callback == nullptr) {
    std::cout << "Must set callback first!" << std::endl;
  } else {
    label_extension_.py_callback->REF_fwd({2.0}, "Source", "A", {1}, {}, 0.0);
    label_extension_.py_callback->REF_bwd({2.0}, "Source", "A", {1}, {}, 0.0);
    label_extension_.py_callback->REF_join({2.0}, {2.0}, "Source", "A", {1});
  }
}

void Search::cleanUp() {
  if (save_nondominated_) {
    const bool& updated_best =
        runDominance(best_labels.get(), direction, elementary);
    // Update heap
    if (updated_best) {
      labelling::makeHeap(unprocessed_labels_.get(), direction);
    }
    // Remove duplicates (just in case)
    best_labels->erase(std::unique(best_labels->begin(), best_labels->end()));
  }
}

/**
 * Private methods
 */
// Initalisations
void Search::initResourceBounds() {
  max_res_curr = max_res;
  // If not all lower bounds are 0, initialise variable min_res_curr to
  // vector of 0s
  bool zeros =
      std::all_of(min_res.begin(), min_res.end(), [](int i) { return i == 0; });
  if (zeros == false) {
    std::vector<double> temp(min_res.size(), 0.0);
    min_res_curr = temp;
  } else
    min_res_curr = min_res;
}

void Search::initContainers() {
  labelling::makeHeap(unprocessed_labels_.get(), direction);
  labelling::makeHeap(best_labels.get(), direction);
}

void Search::initLabels() {
  std::string              node;
  std::vector<double>      res = min_res_curr;
  std::vector<std::string> path;
  if (direction == "forward") {
    node = "Source";
  } else { // backward
    // set monotone resource to upper bound
    res[0] = max_res_curr[0];
    node   = "Sink";
  }
  path          = {node};
  current_label = std::make_shared<labelling::Label>(0.0, node, res, path);
  // Final label dummy init
  node        = "";
  res         = {};
  path        = {""};
  final_label = std::make_shared<labelling::Label>(0.0, node, res, path);
  // Add to best labels.
  // best_labels->push_back(*current_label);
  unprocessed_labels_->push_back(*current_label);
  // update heap sortings
  labelling::pushHeap(unprocessed_labels_.get(), direction);
  // labelling::pushHeap(best_labels.get(), direction);
}

// Advancing the search
void Search::runSearch() {
  updateCurrentLabel();
  updateHalfWayPoints();
  if (!stop) {
    extendCurrentLabel();
    labelling::pushHeap(unprocessed_labels_.get(), direction);
  }
  // Run dominance for all labels (unprocessed + best)
  if (iteration_ % dominance_frequency == 0) {
    auto updated_unprocessed = std::make_unique<bool>();
    auto updated_best        = std::make_unique<bool>();
    *updated_unprocessed     = false;
    *updated_best            = false;
    // auto labels_ = std::make_unique<std::vector<labelling::Label>>();
    // // Allocate memory
    // labels_->reserve(unprocessed_labels_->size() + best_labels->size());
    // labels_->insert(
    //     labels_->end(),
    //     unprocessed_labels_->begin(),
    //     unprocessed_labels_->end());
    // labels_->insert(labels_->end(), best_labels->begin(),
    // best_labels->end()); std::set<labelling::Label> s(labels_->begin(),
    // labels_->end()); labels_->assign(s.begin(), s.end());
    runDominance(
        unprocessed_labels_.get(),
        best_labels.get(),
        updated_unprocessed.get(),
        updated_best.get(),
        direction,
        elementary,
        save_nondominated_);
    // labels_->clear();
    // Update heap
    if (*updated_unprocessed)
      labelling::makeHeap(unprocessed_labels_.get(), direction);
    if (*updated_best && save_nondominated_) {
      labelling::makeHeap(best_labels.get(), direction);
      labelling::pushHeap(best_labels.get(), direction);
    }
  }
  saveCurrentBestLabel();
  ++processed_count;
  ++iteration_;
}

void Search::updateCurrentLabel() {
  if (unprocessed_labels_->size() > 0) {
    // Get next label and removes current_label
    auto new_label_ptr = std::make_shared<labelling::Label>(
        labelling::getNextLabel(unprocessed_labels_.get(), direction));
    // Update current label
    current_label.swap(new_label_ptr);
    ++unprocessed_count;
  } else {
    stop = true;
  }
}

void Search::updateHalfWayPoints() {
  // Update half-way points
  if (direction == "forward")
    min_res_curr[0] = std::max(
        min_res_curr[0],
        std::min(current_label->resource_consumption[0], max_res_curr[0]));
  else
    max_res_curr[0] = std::min(
        max_res_curr[0],
        std::max(current_label->resource_consumption[0], min_res_curr[0]));
  // Check bounds
  if ((direction == "forward" &&
       current_label->resource_consumption[0] <= max_res_curr[0]) ||
      (direction == "backward" &&
       current_label->resource_consumption[0] > min_res_curr[0]))
    ;
  else {
    stop = true;
  }
}

void Search::extendCurrentLabel() {
  // Extract relevant edges
  std::vector<Edge> edges_(graph_ptr->edges.size());
  auto              copy_if_iterator = std::copy_if(
      graph_ptr->edges.begin(),
      graph_ptr->edges.end(),
      edges_.begin(),
      [&](const Edge& e) {
        if (elementary) {
          if (direction == "forward" &&
              std::find(
                  current_label->unreachable_nodes.begin(),
                  current_label->unreachable_nodes.end(),
                  e.head) != current_label->unreachable_nodes.end())
            return false;
          else if (
              direction == "backward" &&
              std::find(
                  current_label->unreachable_nodes.begin(),
                  current_label->unreachable_nodes.end(),
                  e.tail) != current_label->unreachable_nodes.end())
            return false;
        }
        if (direction == "forward")
          return e.tail == current_label->node;
        return e.head == current_label->node;
      });
  edges_.erase(copy_if_iterator, edges_.end());
  // Extend and check current resource feasibility for each edge
  for (Edge e : edges_) {
    label_extension_.extend(
        unprocessed_labels_.get(),
        current_label.get(),
        e,
        direction,
        elementary,
        max_res_curr,
        min_res_curr);
    ++generated_count;
  }
}

void Search::saveCurrentBestLabel() {
  if (final_label->node.empty()) {
    final_label = std::make_shared<labelling::Label>(*current_label);
    return;
  }
  if (!current_label || !current_label->checkFeasibility(max_res, min_res))
    return;
  if (final_label->node == current_label->node &&
      current_label->fullDominance(*final_label, direction, elementary)) {
    final_label = std::make_shared<labelling::Label>(*current_label);
  } else {
    // TODO check
    // First source-sink path
    if ((direction == "forward" &&
         (current_label->partial_path.back() == "Sink" &&
          final_label->node == "Source")) ||
        (direction == "backward" &&
         (current_label->partial_path.back() == "Source" &&
          final_label->node == "Sink")))
      final_label = std::make_shared<labelling::Label>(*current_label);
  }
}

} // namespace bidirectional
