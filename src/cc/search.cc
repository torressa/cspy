#include "search.h"

#include <algorithm> // sort, all_of, find

namespace bidirectional {

// ctor
Search::Search(
    const DiGraph&                   graph_in,
    const std::vector<double>&       max_res_in,
    const std::vector<double>&       min_res_in,
    const std::string&               direction_in,
    const bool&                      elementary_in,
    const std::vector<double>&       lower_bound_weight_in,
    const labelling::LabelExtension& label_extension_in,
    const bool&                      direction_both_in)
    : graph(graph_in),
      max_res(max_res_in),
      min_res(min_res_in),
      direction(direction_in),
      elementary(elementary_in),
      lower_bound_weight(lower_bound_weight_in),
      label_extension_(label_extension_in),
      direction_both_(direction_both_in) {
  unprocessed_labels_ = std::make_unique<std::vector<labelling::Label>>();
  // allocate memory
  efficient_labels.resize(graph.number_vertices);
  best_labels.resize(graph.number_vertices, nullptr);
  // Initalise resource bounds
  initResourceBounds();
  initLabels();
  initContainers();
}

// Default dtor
Search::~Search(){};

void Search::move(const std::vector<double>& current_resource_bound) {
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

void Search::setPrimalBound(const double& new_primal_bound) {
  if (primal_st_bound_ && new_primal_bound < final_label->weight) {
    primal_bound_ = new_primal_bound;
  } else if (
      (primal_bound_set_ && new_primal_bound < primal_bound_) ||
      !primal_bound_set_) {
    primal_bound_     = new_primal_bound;
    primal_bound_set_ = true;
  }
}

void Search::cleanUp() {
  for (const int n : visited_vertices) {
    if (efficient_labels[n].size() > 0) {
      if (direction == "forward") {
        std::sort(efficient_labels[n].begin(), efficient_labels[n].end());
      } else {
        std::sort(
            efficient_labels[n].begin(),
            efficient_labels[n].end(),
            std::greater<>{});
      }
    }
  }
}

bool Search::checkVertexVisited(const int& vertex_idx) const {
  return (visited_vertices.find(vertex_idx) != visited_vertices.end());
}

double Search::getHalfWayPoint() const {
  return max_res_curr[0];
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
}

void Search::initLabels() {
  Vertex                   vertex;
  std::vector<double>      res = min_res_curr;
  std::vector<std::string> path;
  if (direction == "forward") {
    vertex = graph.source;
  } else { // backward
    // set monotone resource to upper bound
    res[0] = max_res_curr[0];
    vertex = graph.sink;
  }
  path          = {vertex.id};
  current_label = std::make_shared<labelling::Label>(0.0, vertex, res, path);
  // Final label dummy init
  Vertex dum_vertex = {"", -1};
  res               = {};
  path              = {""};
  final_label = std::make_shared<labelling::Label>(0.0, dum_vertex, res, path);
  // updateEfficientLabels();
  unprocessed_labels_->push_back(*current_label);
  // update heap
  labelling::pushHeap(unprocessed_labels_.get(), direction);
  // Add to efficient and best labels
  efficient_labels[vertex.idx].push_back(*current_label);
  best_labels[vertex.idx] = std::make_shared<labelling::Label>(*current_label);
  // Update vertices visited
  visited_vertices.insert(vertex.idx);
}

// Advancing the search
void Search::runSearch() {
  updateCurrentLabel();
  updateHalfWayPoints();
  if (!stop) {
    extendCurrentLabel();
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
  if (direction == "forward") {
    min_res_curr[0] = std::max(
        min_res_curr[0],
        std::min(current_label->resource_consumption[0], max_res_curr[0]));
  } else {
    max_res_curr[0] = std::min(
        max_res_curr[0],
        std::max(current_label->resource_consumption[0], min_res_curr[0]));
  }
  // Check resource bounds
  if ((direction == "forward" &&
       current_label->resource_consumption[0] <= max_res_curr[0]) ||
      (direction == "backward" &&
       current_label->resource_consumption[0] > min_res_curr[0]))
    ;
  // only stop if search is being performed in both directions
  else if (direction_both_) {
    stop = true;
  }
}

void Search::extendCurrentLabel() {
  // Extend and check current resource feasibility for each edge
  std::vector<AdjVertex> adj_vertices;
  if (direction == "forward") {
    adj_vertices = graph.adjacency_list[current_label->vertex.idx];
  } else {
    adj_vertices = graph.reversed_adjacency_list[current_label->vertex.idx];
  }
  // for each adjacent vertex (successors if forward predecessors if backward)
  for (std::vector<AdjVertex>::const_iterator it = adj_vertices.begin();
       it != adj_vertices.end();
       ++it) {
    const AdjVertex& adj_vertex = *it;
    // If (node reachable | non elementary)
    if ((elementary &&
         std::find(
             current_label->unreachable_nodes.begin(),
             current_label->unreachable_nodes.end(),
             adj_vertex.vertex.id) == current_label->unreachable_nodes.end()) ||
        !elementary) {
      // extend current label along edge
      labelling::Label new_label = label_extension_.extend(
          current_label.get(),
          adj_vertex,
          direction,
          elementary,
          max_res_curr,
          min_res_curr);
      // If label non-empty, (only when the extension is resource-feasible)
      if (!new_label.vertex.id.empty()) {
        updateEfficientLabels(adj_vertex.vertex.idx, new_label);
      }
    }
  }
}

void Search::updateEfficientLabels(
    const int&              vertex_idx,
    const labelling::Label& candidate_label) {
  // ref efficient_labels_ for a given vertex
  std::vector<labelling::Label>& efficient_labels_vertex =
      efficient_labels[vertex_idx];
  if (!candidate_label.vertex.id.empty()) {
    if (std::find(
            efficient_labels_vertex.begin(),
            efficient_labels_vertex.end(),
            candidate_label) == efficient_labels_vertex.end()) {
      ++generated_count;
      // If there already exists labels for the given vertex
      if (efficient_labels_vertex.size() > 1) {
        // check if new_label is dominated by any other comparable label
        const bool dominated = runDominanceEff(
            &efficient_labels_vertex, candidate_label, direction, elementary);
        if (!dominated && !checkPrimalBound(candidate_label)) {
          // add candidate_label to efficient_labels and unprocessed heap
          efficient_labels_vertex.push_back(candidate_label);
          unprocessed_labels_->push_back(candidate_label);
          labelling::pushHeap(unprocessed_labels_.get(), direction);
        }
      }
      // First label produced for the vertex
      else {
        // update both efficient and unprocessed labels
        efficient_labels_vertex.push_back(candidate_label);
        unprocessed_labels_->push_back(candidate_label);
        labelling::pushHeap(unprocessed_labels_.get(), direction);
      }
      updateBestLabels(vertex_idx, candidate_label);
      // Update vertices visited
      visited_vertices.insert(vertex_idx);
    }
  }
}

void Search::updateBestLabels(
    const int&              vertex_idx,
    const labelling::Label& candidate_label) {
  // Only save full paths when they are global resource feasible
  if (direction == "foward" && vertex_idx == graph.sink.idx &&
      !candidate_label.checkFeasibility(max_res, min_res)) {
    return;
  } else if (
      direction == "backward" && vertex_idx == graph.source.idx &&
      !candidate_label.checkFeasibility(max_res, min_res)) {
    return;
  }
  // Update best_label only when new label has lower weight or first label
  if (best_labels[vertex_idx] &&
      candidate_label.weight < best_labels[vertex_idx]->weight) {
    best_labels[vertex_idx] =
        std::make_shared<labelling::Label>(candidate_label);
  } else if (!best_labels[vertex_idx]) {
    // If not already exists
    best_labels[vertex_idx] =
        std::make_shared<labelling::Label>(candidate_label);
  }
}

void Search::saveCurrentBestLabel() {
  if (final_label->vertex.id.empty()) {
    final_label = std::make_shared<labelling::Label>(*current_label);
    return;
  }
  // Check for global feasibility
  if (!current_label->checkFeasibility(max_res, min_res)) {
    return;
  }
  if (final_label->vertex.idx == current_label->vertex.idx &&
      current_label->fullDominance(*final_label, direction, elementary)) {
    final_label = std::make_shared<labelling::Label>(*current_label);
  } else {
    // First source-sink path
    if ((direction == "forward" &&
         (current_label->partial_path.back() == "Sink" &&
          final_label->vertex.id == "Source")) ||
        (direction == "backward" &&
         (current_label->partial_path.back() == "Source" &&
          final_label->vertex.id == "Sink"))) {
      final_label      = std::make_shared<labelling::Label>(*current_label);
      primal_st_bound_ = true;
    }
  }
}

bool Search::checkPrimalBound(const labelling::Label& candidate_label) const {
  if ((primal_st_bound_ && candidate_label.weight >= final_label->weight) ||
      (primal_bound_set_ && candidate_label.weight >= primal_bound_)) {
    // + lower_bound_weight[candidate_label.vertex.idx]
    return true;
  }
  return false;
}

} // namespace bidirectional
