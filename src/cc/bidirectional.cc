#include "bidirectional.h"

#include <algorithm> // sort, all_of, find

#include "preprocessing.h" // shortest_path, INF

namespace bidirectional {

/* Public methods */

BiDirectional::BiDirectional(
    const int&                 number_vertices,
    const int&                 number_edges,
    const int&                 source_id,
    const int&                 sink_id,
    const std::vector<double>& max_res_in,
    const std::vector<double>& min_res_in)
    : max_res(max_res_in),
      min_res(min_res_in),
      graph_ptr_(std::make_unique<DiGraph>(
          number_vertices,
          number_edges,
          source_id,
          sink_id)),
      label_extension_(std::make_unique<labelling::LabelExtension>()) {}

void BiDirectional::setREFCallback(bidirectional::REFCallback* cb) const {
  label_extension_->setREFCallback(cb);
}

std::vector<int> BiDirectional::getPath() const {
  return best_label_->partial_path;
}

std::vector<double> BiDirectional::getConsumedResources() const {
  return best_label_->resource_consumption;
}

double BiDirectional::getTotalCost() const {
  return best_label_->weight;
}

void BiDirectional::run() {
  start_time_ = std::chrono::system_clock::now();
  initSearches();
  runPreprocessing();
  while (stop_[0] == false || stop_[1] == false) {
    const std::string& direction_ = getDirection();
    int                direction_idx;
    if (options.direction != "both")
      direction_idx = 0;
    else if (direction_ == "forward")
      direction_idx = 0;
    else
      direction_idx = 1;
    if (!direction_.empty()) {
      move(direction_idx);
    } else {
      break;
    }
    if (terminate(direction_idx, *intermediate_label_[direction_idx])) {
      break;
    }
  }
  postProcessing();
}

/* Private methods */

void BiDirectional::runPreprocessing() {
  // if (options.direction == "both" || options.direction == "backward" ||
  //     options.bounds_pruning) {
  //   graph_ptr_->initReversedAdjList();
  // }
  if (options.bounds_pruning) {
    if (options.direction == "both" || options.direction == "forward") {
      shortest_path(lower_bound_weight_[0].get(), *graph_ptr_, true);
    }
    if (options.direction == "both" || options.direction == "backward") {
      shortest_path(lower_bound_weight_[1].get(), *graph_ptr_, false);
    }
  }
}

void BiDirectional::initSearches() {
  if (options.direction == "both") {
    directions_.push_back("forward");
    directions_.push_back("backward");
  } else {
    directions_.push_back(options.direction);
  }
  directions_size_ = directions_.size();
  // allocate memory
  stop_.resize(directions_size_, false);
  unprocessed_count_.resize(directions_size_, 0);
  processed_count_.resize(directions_size_, 0);
  generated_count_.resize(directions_size_, 0);

  lower_bound_weight_.resize(directions_size_);
  visited_vertices_.resize(directions_size_);

  current_label_.resize(directions_size_);
  intermediate_label_.resize(directions_size_);
  efficient_labels_.resize(directions_size_);
  best_labels_.resize(directions_size_);
  unprocessed_labels_.resize(directions_size_);

  for (int s = 0; s < directions_size_; ++s) {
    lower_bound_weight_[s] = std::make_unique<std::vector<double>>();
    lower_bound_weight_[s]->resize(graph_ptr_->number_vertices, 0.0);
    unprocessed_labels_[s] = std::make_unique<std::vector<labelling::Label>>();
    efficient_labels_[s].resize(graph_ptr_->number_vertices);
    best_labels_[s].resize(graph_ptr_->number_vertices, nullptr);
  }

  // Initialise resource bounds
  initResourceBounds();
  // Initialise labels
  labelling::Label label(0.0, {-1, -1}, {}, {});
  best_label_ = std::make_shared<labelling::Label>(label);
  for (int s = 0; s < directions_size_; ++s) {
    initLabels(s);
  }
  // Init other containers (labels heaps)
  initContainers();
}

void BiDirectional::initResourceBounds() {
  max_res_curr_ = max_res;
  // If not all lower bounds are 0, initialise variable min_res_curr to
  // vector of 0s
  bool zeros =
      std::all_of(min_res.begin(), min_res.end(), [](int i) { return i == 0; });
  if (zeros == false) {
    std::vector<double> temp(min_res.size(), 0.0);
    min_res_curr_ = temp;
  } else {
    min_res_curr_ = min_res;
  }
}

void BiDirectional::initLabels(const int& direction_idx) {
  Vertex              vertex;
  std::vector<double> res = min_res_curr_;
  std::vector<int>    path;

  if (directions_[direction_idx] == "forward") {
    vertex = graph_ptr_->source;
  } else { // backward
    // set monotone resource to upper bound
    res[0] = max_res_curr_[0];
    vertex = graph_ptr_->sink;
  }
  path = {vertex.user_id};
  current_label_[direction_idx] =
      std::make_shared<labelling::Label>(0.0, vertex, res, path);
  // Final label dummy init
  Vertex dum_vertex = {-1, -1};
  res               = {};
  path              = {};
  intermediate_label_[direction_idx] =
      std::make_shared<labelling::Label>(0.0, dum_vertex, res, path);
  // updateEfficientLabels();
  // unprocessed_labels_[direction_idx]->push_back(*current_label_[direction_idx]);
  // update heap
  labelling::pushHeap(
      unprocessed_labels_[direction_idx].get(), directions_[direction_idx]);
  // Add to efficient and best labels
  efficient_labels_[direction_idx][vertex.lemon_id].push_back(
      *current_label_[direction_idx]);
  best_labels_[direction_idx][vertex.lemon_id] =
      std::make_shared<labelling::Label>(*current_label_[direction_idx]);
  // Update vertices visited
  visited_vertices_[direction_idx].insert(vertex.lemon_id);
}

void BiDirectional::initContainers() {
  if (options.direction != "both") {
    labelling::makeHeap(unprocessed_labels_[0].get(), options.direction);
  } else {
    for (int s = 0; s < directions_size_; ++s) {
      labelling::makeHeap(unprocessed_labels_[s].get(), directions_[s]);
    }
  }
}

/**
 * Private methods
 */
// Initialisations

std::string BiDirectional::getDirection() const {
  if (options.direction == "both") {
    if (!stop_[0] && stop_[1]) {
      return "forward";
    } else if (stop_[0] && !stop_[1]) {
      return "backward";
    } else if (!stop_[0] && !stop_[1]) {
      // TODO: fix random
      // if (method == "random") {
      //   // return a random direction
      //   const std::vector<std::string> directions = {"forward",
      //   "backward"}; const int                      r          =
      //   std::rand() % 2; const std::string&             direction  =
      //   directions[r]; return direction;
      // } else
      if (options.method == "generated") {
        // return direction with least number of generated labels
        if (generated_count_[0] < generated_count_[1]) {
          return "forward";
        }
        return "backward";
      } else if (options.method == "processed") {
        // return direction with least number of processed labels
        if (processed_count_[0] < processed_count_[1]) {
          return "forward";
        }
        return "backward";
      } else if (options.method == "unprocessed") {
        // return direction with least number of unprocessed labels
        if (unprocessed_count_[0] < unprocessed_count_[1]) {
          return "forward";
        }
        return "backward";
      }
    } else {
      ;
    }
  } else {
    // Single direction
    if (options.direction == "forward" && stop_[0]) {
      ;
    } else if (options.direction == "backward" && stop_[0]) {
      ;
    } else {
      return options.direction;
    }
  }
  return "";
}

void BiDirectional::move(const int& direction_idx) {
  const bool& bounds_exceeded = checkBounds(direction_idx);
  if (!bounds_exceeded) {
    extendCurrentLabel(direction_idx);
    saveCurrentBestLabel(direction_idx);
  } else {
    stop_[direction_idx] = true;
  }
  updateHalfWayPoints(direction_idx);
  updateCurrentLabel(direction_idx);
  ++processed_count_[direction_idx];
  ++iteration_;
}

bool BiDirectional::terminate(
    const int&              direction_idx,
    const labelling::Label& label) {
  // Check time elapsed (if relevant)
  std::chrono::duration<double> duration =
      (std::chrono::system_clock::now() - start_time_);
  double timediff_sec = duration.count();
  if (!std::isnan(options.time_limit) && timediff_sec >= options.time_limit) {
    return true;
  }
  // Check input label
  return checkValidLabel(direction_idx, label);
}

bool BiDirectional::checkValidLabel(
    const int&              direction_idx,
    const labelling::Label& label) {
  if (label.vertex.lemon_id != -1 &&
      label.checkStPath(graph_ptr_->source.user_id, graph_ptr_->sink.user_id)) {
    if (!std::isnan(options.threshold) &&
        label.checkThreshold(options.threshold)) {
      terminated_early_w_st_path_               = true;
      terminated_early_w_st_path_direction_idx_ = direction_idx;
      return true;
    }
  }
  return false;
}

void BiDirectional::updateCurrentLabel(const int& direction_idx) {
  if (unprocessed_labels_[direction_idx]->size() > 0) {
    // Get next label and removes current_label from heap
    auto new_label_ptr =
        std::make_shared<labelling::Label>(labelling::getNextLabel(
            unprocessed_labels_[direction_idx].get(),
            directions_[direction_idx]));
    // swap current label with new label
    current_label_[direction_idx].swap(new_label_ptr);
    // Update unprocessed label counter
    unprocessed_count_[direction_idx] =
        unprocessed_labels_[direction_idx]->size();
  } else {
    stop_[direction_idx] = true;
  }
}

bool BiDirectional::checkBounds(const int& direction_idx) {
  const std::string& direction_ = directions_[direction_idx];
  // Check resource bounds
  if ((direction_ == "forward" &&
       current_label_[direction_idx]->resource_consumption[0] <=
           max_res_curr_[0]) ||
      (direction_ == "backward" &&
       current_label_[direction_idx]->resource_consumption[0] >
           min_res_curr_[0]) ||
      max_res_curr_[0] != min_res_curr_[0]) {
    return false;
  }
  // only stop if search is being performed in both directions
  else if (options.direction == "both") {
    return true;
  }
  return false;
}
void BiDirectional::updateHalfWayPoints(const int& direction_idx) {
  const std::string& direction_ = directions_[direction_idx];
  if (direction_ == "forward") {
    min_res_curr_[0] = std::max(
        min_res_curr_[0],
        std::min(
            current_label_[direction_idx]->resource_consumption[0],
            max_res_curr_[0]));
  } else {
    max_res_curr_[0] = std::min(
        max_res_curr_[0],
        std::max(
            current_label_[direction_idx]->resource_consumption[0],
            min_res_curr_[0]));
  }
}

void BiDirectional::extendCurrentLabel(const int& direction_idx) {
  // Extend and check current resource feasibility for each edge
  const std::string&                 direction_ = directions_[direction_idx];
  std::shared_ptr<labelling::Label>& current_label =
      current_label_[direction_idx];
  if (direction_ == "forward") {
    // For each outgoing arc from the current label
    for (LemonGraph::OutArcIt a(
             *graph_ptr_->lemon_graph_ptr,
             graph_ptr_->getLNodeFromId(current_label->vertex.lemon_id));
         a != lemon::INVALID;
         ++a) {
      extendSingleLabel(
          current_label.get(),
          direction_idx,
          graph_ptr_->getAdjVertex(a, true));
    }
  } else {
    // For each incoming arc to the current label
    for (LemonGraph::InArcIt a(
             *graph_ptr_->lemon_graph_ptr,
             graph_ptr_->getLNodeFromId(current_label->vertex.lemon_id));
         a != lemon::INVALID;
         ++a) {
      extendSingleLabel(
          current_label.get(),
          direction_idx,
          graph_ptr_->getAdjVertex(a, false));
    }
  }
}

void BiDirectional::extendSingleLabel(
    labelling::Label* label,
    const int&        direction_idx,
    const AdjVertex&  adj_vertex) {
  const std::string& direction_ = directions_[direction_idx];
  if ((options.elementary &&
       std::find(
           label->unreachable_nodes.begin(),
           label->unreachable_nodes.end(),
           adj_vertex.vertex.user_id) == label->unreachable_nodes.end()) ||
      !options.elementary) {
    // extend current label along edge
    labelling::Label new_label = label_extension_->extend(
        label,
        adj_vertex,
        direction_,
        options.elementary,
        max_res_curr_,
        min_res_curr_);
    // If label non-empty, (only when the extension is resource-feasible)
    if (new_label.vertex.lemon_id != -1) {
      updateEfficientLabels(direction_idx, new_label);
    }
  }
}

void BiDirectional::updateEfficientLabels(
    const int&              direction_idx,
    const labelling::Label& candidate_label) {
  const std::string& direction_ = directions_[direction_idx];
  // const ref vertex index
  const int& vertex_idx = candidate_label.vertex.lemon_id;
  // ref efficient_labels_ for a given vertex
  std::vector<labelling::Label>& efficient_labels_vertex =
      efficient_labels_[direction_idx][vertex_idx];
  std::unique_ptr<std::vector<labelling::Label>>& unprocessed_labels_ptr =
      unprocessed_labels_[direction_idx];
  if (candidate_label.vertex.lemon_id != -1) {
    if (std::find(
            efficient_labels_vertex.begin(),
            efficient_labels_vertex.end(),
            candidate_label) == efficient_labels_vertex.end()) {
      ++generated_count_[direction_idx];
      // If there already exists labels for the given vertex
      if (efficient_labels_vertex.size() > 1) {
        // check if new_label is dominated by any other comparable label
        const bool dominated = runDominanceEff(
            &efficient_labels_vertex,
            candidate_label,
            direction_,
            options.elementary);
        if (!dominated && !checkPrimalBound(direction_idx, candidate_label)) {
          // add candidate_label to efficient_labels and unprocessed heap
          efficient_labels_vertex.push_back(candidate_label);
          unprocessed_labels_ptr->push_back(candidate_label);
          labelling::pushHeap(unprocessed_labels_ptr.get(), direction_);
        }
      }
      // First label produced for the vertex
      else {
        // update both efficient and unprocessed labels
        efficient_labels_vertex.push_back(candidate_label);
        unprocessed_labels_ptr->push_back(candidate_label);
        labelling::pushHeap(unprocessed_labels_ptr.get(), direction_);
      }
      updateBestLabels(direction_idx, candidate_label);
      // Update vertices visited
      visited_vertices_[direction_idx].insert(vertex_idx);
    }
  }
}

void BiDirectional::updateBestLabels(
    const int&              direction_idx,
    const labelling::Label& candidate_label) {
  // Only save full paths when they are global resource feasible
  const int&         vertex_idx = candidate_label.vertex.lemon_id;
  const std::string& direction_ = directions_[direction_idx];
  std::vector<std::shared_ptr<labelling::Label>>& best_labels =
      best_labels_[direction_idx];

  if (direction_ == "forward" && vertex_idx == graph_ptr_->sink.lemon_id &&
      !candidate_label.checkFeasibility(max_res, min_res)) {
    return;
  } else if (
      direction_ == "backward" && vertex_idx == graph_ptr_->source.lemon_id &&
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

void BiDirectional::saveCurrentBestLabel(const int& direction_idx) {
  const std::string&                 direction_ = directions_[direction_idx];
  std::shared_ptr<labelling::Label>& intermediate_label_ptr =
      intermediate_label_[direction_idx];
  std::shared_ptr<labelling::Label>& current_label_ptr =
      current_label_[direction_idx];

  if (intermediate_label_ptr->vertex.lemon_id == -1) {
    intermediate_label_ptr =
        std::make_shared<labelling::Label>(*current_label_ptr);
    return;
  }
  // Check for global feasibility
  if (!current_label_ptr->checkFeasibility(max_res, min_res)) {
    return;
  }
  if (intermediate_label_ptr->vertex.lemon_id ==
          current_label_ptr->vertex.lemon_id &&
      current_label_ptr->fullDominance(
          *intermediate_label_ptr, direction_, options.elementary)) {
    intermediate_label_ptr =
        std::make_shared<labelling::Label>(*current_label_ptr);
  } else {
    // First source-sink path
    if ((direction_ == "forward" &&
         (current_label_ptr->partial_path.back() == graph_ptr_->sink.user_id &&
          intermediate_label_ptr->vertex.user_id ==
              graph_ptr_->source.user_id)) ||
        (direction_ == "backward" && (current_label_ptr->partial_path.back() ==
                                          graph_ptr_->source.user_id &&
                                      intermediate_label_ptr->vertex.user_id ==
                                          graph_ptr_->sink.user_id))) {
      // Save complete source-sink path
      intermediate_label_ptr =
          std::make_shared<labelling::Label>(*current_label_ptr);
      // Update bounds
      if (std::isnan(primal_st_bound_) ||
          intermediate_label_ptr->weight < primal_st_bound_) {
        primal_st_bound_ = intermediate_label_ptr->weight;
      }
    }
  }
}

bool BiDirectional::checkPrimalBound(
    const int&              direction_idx,
    const labelling::Label& candidate_label) const {
  const std::unique_ptr<std::vector<double>>& lower_bound_weight =
      lower_bound_weight_[direction_idx];
  if (!options.bounds_pruning) {
    return false;
  }
  if (!std::isnan(primal_st_bound_) &&
      candidate_label.weight +
              (*lower_bound_weight)[candidate_label.vertex.lemon_id] >
          primal_st_bound_) {
    return true;
  }
  return false;
}

/**
 * Post-processing methods
 */

void BiDirectional::postProcessing() {
  if (!terminated_early_w_st_path_) {
    if (options.direction == "both") {
      // If bidirectional algorithm used and both directions traversed, run path
      // joining procedure.
      joinLabels();
    } else {
      // If forward direction specified or backward direction not traversed
      if (options.direction == "forward") {
        // Forward
        best_label_ =
            std::make_shared<labelling::Label>(*intermediate_label_[0]);
      }
      // If backward direction specified or forward direction not traversed
      else {
        // Backward
        best_label_ =
            std::make_shared<labelling::Label>(labelling::processBwdLabel(
                *intermediate_label_[0], max_res, min_res, true));
      }
    }
  } else {
    // final label contains the label that triggered the early termination
    const std::string& direction_ =
        directions_[terminated_early_w_st_path_direction_idx_];
    if (direction_ == "forward") {
      best_label_ = std::make_shared<labelling::Label>(
          *intermediate_label_[terminated_early_w_st_path_direction_idx_]);
    } else {
      best_label_ =
          std::make_shared<labelling::Label>(labelling::processBwdLabel(
              *intermediate_label_[terminated_early_w_st_path_direction_idx_],
              max_res,
              min_res,
              true));
    }
  }
}

double BiDirectional::getUB() {
  double UB = INF;
  // Extract forward and backward best labels (one's with least weight)
  const auto& fwd_best = best_labels_[0][graph_ptr_->sink.lemon_id];
  const auto& bwd_best = best_labels_[1][graph_ptr_->source.lemon_id];
  // Upper bound must be a resource-feasible s-t path
  if (fwd_best && fwd_best->checkFeasibility(max_res, min_res)) {
    UB = fwd_best->weight;
  }
  if (bwd_best && bwd_best->checkFeasibility(max_res, min_res)) {
    if (bwd_best->weight < UB) {
      UB = bwd_best->weight;
    }
  }
  return UB;
}

void BiDirectional::getMinimumWeights(double* fwd_min, double* bwd_min) {
  // Forward
  // init
  *fwd_min = INF;
  for (const int& n : visited_vertices_[0]) {
    if (n != graph_ptr_->source.lemon_id && best_labels_[0][n] &&
        best_labels_[0][n]->weight < *fwd_min) {
      *fwd_min = best_labels_[0][n]->weight;
    }
  }
  // backward
  *bwd_min = INF;
  for (const int& n : visited_vertices_[1]) {
    if (n != graph_ptr_->sink.lemon_id && best_labels_[1][n] &&
        best_labels_[1][n]->weight < *bwd_min) {
      *bwd_min = best_labels_[1][n]->weight;
    }
  }
}

bool BiDirectional::checkVertexVisited(
    const int& direction_idx,
    const int& vertex_idx) const {
  return (
      visited_vertices_[direction_idx].find(vertex_idx) !=
      visited_vertices_[direction_idx].end());
}

void BiDirectional::cleanUp() {
  for (int s = 0; s < directions_size_; ++s) {
    const std::string& direction_ = directions_[s];
    for (const int n : visited_vertices_[s]) {
      if (efficient_labels_[n].size() > 0) {
        if (direction_ == "forward") {
          std::sort(
              efficient_labels_[s][n].begin(), efficient_labels_[s][n].end());
        } else {
          std::sort(
              efficient_labels_[s][n].begin(),
              efficient_labels_[s][n].end(),
              std::greater<>{});
        }
      }
    }
  }
}

void BiDirectional::joinLabels() {
  // one can sort the labels prior to joining then use this to break joining but
  // it takes too long
  // cleanUp();
  // upper bound on source-sink path
  double        UB      = getUB();
  const double& HF      = std::min(max_res_curr_[0], min_res_curr_[0]);
  auto          fwd_min = std::make_unique<double>();
  auto          bwd_min = std::make_unique<double>();
  // lower bounds on forward and backward labels
  getMinimumWeights(fwd_min.get(), bwd_min.get());

  std::vector<labelling::Label> merged_labels_;

  // for each vertex visited forward
  for (const int& n : visited_vertices_[0]) {
    // if bound check fwd_label
    if (best_labels_[0][n]->weight + *bwd_min <= UB &&
        n != graph_ptr_->sink.lemon_id) {
      // for each forward label at n
      for (auto fwd_iter = efficient_labels_[0][n].cbegin();
           fwd_iter != efficient_labels_[0][n].cend();
           ++fwd_iter) {
        const labelling::Label& fwd_label = *fwd_iter;
        // if bound check fwd_label
        if (fwd_label.resource_consumption[0] <= HF &&
            fwd_label.weight + *bwd_min <= UB) {
          // for each successor of n
          for (LemonGraph::OutArcIt a(
                   *graph_ptr_->lemon_graph_ptr, graph_ptr_->getLNodeFromId(n));
               a != lemon::INVALID;
               ++a) {
            const int&    m           = graph_ptr_->getId(graph_ptr_->head(a));
            const double& edge_weight = graph_ptr_->getWeight(a);
            if (checkVertexVisited(1, m) && m != graph_ptr_->source.lemon_id &&
                (fwd_label.weight + edge_weight + best_labels_[1][m]->weight <=
                 UB)) {
              // for each backward label at m
              for (auto bwd_iter = efficient_labels_[1][m].cbegin();
                   bwd_iter != efficient_labels_[1][m].cend();
                   ++bwd_iter) {
                const labelling::Label& bwd_label = *bwd_iter;
                // TODO: should suffice with strict > HF, but Beasley 10 fails
                if (bwd_label.resource_consumption[0] >= HF &&
                    (fwd_label.weight + edge_weight + bwd_label.weight <= UB) &&
                    labelling::mergePreCheck(
                        fwd_label, bwd_label, max_res, options.elementary)) {
                  const labelling::Label& merged_label = labelling::mergeLabels(
                      fwd_label,
                      bwd_label,
                      *label_extension_,
                      graph_ptr_->getAdjVertex(a, true),
                      graph_ptr_->sink,
                      max_res,
                      min_res);
                  if (merged_label.vertex.lemon_id != -1 &&
                      merged_label.checkFeasibility(max_res, min_res) &&
                      labelling::halfwayCheck(merged_label, merged_labels_)) {
                    if (best_label_->vertex.lemon_id == -1 ||
                        (merged_label.fullDominance(
                             *best_label_, "forward", options.elementary) ||
                         merged_label.weight < best_label_->weight)) {
                      // Save
                      best_label_ =
                          std::make_shared<labelling::Label>(merged_label);
                      // Tighten UB
                      if (best_label_->weight < UB) {
                        UB = best_label_->weight;
                      }
                      // Stop if time out or threshold found
                      if (terminate(0, *best_label_)) {
                        return;
                      }
                    }
                  }
                  // Add merged label to list
                  merged_labels_.push_back(merged_label);
                }
              }
            }
          }
        }
      }
    }
  }
} // end joinLabels

} // namespace bidirectional
