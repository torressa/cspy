#include "bidirectional.h"

#include "preprocessing.h" // dijkstra, INF

namespace bidirectional {

BiDirectional::BiDirectional(
    const int&                 number_vertices,
    const int&                 number_edges,
    const std::vector<double>& max_res_in,
    const std::vector<double>& min_res_in)
    : max_res(max_res_in),
      min_res(min_res_in),
      graph(new DiGraph(number_vertices, number_edges)),
      label_extension_(std::make_unique<labelling::LabelExtension>()),
      lower_bound_weight_fwd_(std::make_unique<std::vector<double>>()),
      lower_bound_weight_bwd_(std::make_unique<std::vector<double>>()) {
  // allocate memory
  lower_bound_weight_fwd_->resize(number_vertices, 0.0);
  lower_bound_weight_bwd_->resize(number_vertices, 0.0);

  Vertex           vertex = {"", -1};
  labelling::Label label(0.0, vertex, {}, {});
  best_label_ = std::make_shared<labelling::Label>(label);
}

BiDirectional::~BiDirectional() {
  graph = nullptr;
  delete graph;
}

void BiDirectional::setREFCallback(bidirectional::REFCallback* cb) const {
  label_extension_->setREFCallback(cb);
}

std::vector<std::string> BiDirectional::getPath() const {
  return best_label_->partial_path;
}

std::vector<double> BiDirectional::getConsumedResources() const {
  return best_label_->resource_consumption;
}

double BiDirectional::getTotalCost() const {
  return best_label_->weight;
}

void BiDirectional::addEdge(
    const std::string&         tail,
    const std::string&         head,
    const double&              weight,
    const std::vector<double>& resource_consumption) {
  graph->addEdge(tail, head, weight, resource_consumption);
}

void BiDirectional::run() {
  start_time_ = clock();
  // Run dijkstra's to get lower bounds
  // Init revesed edge list (if required)
  if (direction == "both" || direction == "backward" || primal_bound) {
    graph->initReversedAdjList();
  }
  if (primal_bound) {
    dijkstra(lower_bound_weight_fwd_.get(), *graph, true);
    dijkstra(lower_bound_weight_bwd_.get(), *graph, false);
  }
  // Init search classes using lower_bound_weight_ + others
  initSearches();
  while (!fwd_search_->stop || !bwd_search_->stop) {
    const std::string next_direction = getDirection();
    if (!next_direction.empty()) {
      move(next_direction);
      updateIntermediateLabel();
    } else {
      break;
    }
    if (terminate(*intermediate_label_)) {
      break;
    }
  }
  if (!terminated_early_w_st_path_) {
    postProcessing();
  } else {
    // final label contains the label that triggered the early termination
    best_label_ = std::make_shared<labelling::Label>(*intermediate_label_);
  }
}

void BiDirectional::initSearches() {
  // Init forward search
  fwd_search_ = std::make_unique<Search>(
      *graph,
      max_res,
      min_res,
      "forward",
      elementary,
      *lower_bound_weight_fwd_,
      *label_extension_,
      (direction == "both"));
  // Init backward search
  bwd_search_ = std::make_unique<Search>(
      *graph,
      max_res,
      min_res,
      "backward",
      elementary,
      *lower_bound_weight_bwd_,
      *label_extension_,
      (direction == "both"));
}

/**
 * Private methods
 */
// Initalisations

std::string BiDirectional::getDirection() const {
  if (direction == "both") {
    if (!fwd_search_->stop && bwd_search_->stop) {
      return "forward";
    } else if (fwd_search_->stop && !bwd_search_->stop) {
      return "backward";
    } else if (!fwd_search_->stop && !bwd_search_->stop) {
      if (method == "random") {
        // return a random direction
        const std::vector<std::string> directions = {"forward", "backward"};
        const int                      r          = std::rand() % 2;
        const std::string&             direction  = directions[r];
        return direction;
      } else if (method == "generated") {
        // return direction with least number of generated labels
        if (fwd_search_->generated_count < bwd_search_->generated_count)
          return "forward";
        return "backward";
      } else if (method == "processed") {
        // return direction with least number of processed labels
        if (fwd_search_->processed_count < bwd_search_->processed_count)
          return "forward";
        return "backward";
      } else if (method == "unprocessed") {
        // return direction with least number of unprocessed labels
        if (fwd_search_->unprocessed_count < bwd_search_->unprocessed_count)
          return "forward";
        return "backward";
      }
    } else {
      ;
    }
  } else {
    // Single direction
    if (direction == "forward" && fwd_search_->stop) {
      ;
    } else if (direction == "backward" && bwd_search_->stop) {
      ;
    } else {
      return direction;
    }
  }
  return "";
}

void BiDirectional::move(const std::string& direction_) {
  if (direction_ == "forward" && !fwd_search_->stop) {
    fwd_search_->move(bwd_search_->max_res_curr);
    // Set primal bound
    if (!bwd_search_->final_label->vertex.id.empty() &&
        bwd_search_->final_label->checkStPath()) {
      fwd_search_->setPrimalBound(bwd_search_->final_label->weight);
    }
  } else if (direction_ == "backward" && !bwd_search_->stop) {
    bwd_search_->move(fwd_search_->min_res_curr);
    // Set primal bound
    if (!fwd_search_->final_label->vertex.id.empty() &&
        fwd_search_->final_label->checkStPath()) {
      bwd_search_->setPrimalBound(fwd_search_->final_label->weight);
    }
  }
}

void BiDirectional::updateIntermediateLabel() {
  if (direction == "forward") {
    intermediate_label_ =
        std::make_shared<labelling::Label>(*fwd_search_->final_label);
  } else if (direction == "backward") {
    intermediate_label_ =
        std::make_shared<labelling::Label>(*bwd_search_->final_label);
  } else {
    if (!fwd_search_->final_label->vertex.id.empty()) {
      intermediate_label_ =
          std::make_shared<labelling::Label>(*fwd_search_->final_label);
    } else if (!bwd_search_->final_label->vertex.id.empty()) {
      intermediate_label_ =
          std::make_shared<labelling::Label>(*bwd_search_->final_label);
    }
  }
}

bool BiDirectional::terminate(const labelling::Label& label) {
  clock_t timediff     = clock() - start_time_;
  double  timediff_sec = ((double)timediff) / CLOCKS_PER_SEC;
  if (!std::isnan(time_limit) && timediff_sec >= time_limit) {
    return true;
  }
  return checkValidLabel(label);
}

bool BiDirectional::checkValidLabel(const labelling::Label& label) {
  if (!label.vertex.id.empty() && label.checkStPath()) {
    if (!std::isnan(threshold) && label.checkThreshold(threshold)) {
      terminated_early_w_st_path_ = true;
      return true;
    }
  }
  return false;
}

void BiDirectional::postProcessing() {
  if (direction == "both") {
    // If bidirectional algorithm used and both directions traversed, run path
    // joining procedure.
    joinLabels();
  } else {
    // If forward direction specified or backward direction not traversed
    if (direction == "forward") {
      // Forward
      best_label_ = std::make_shared<labelling::Label>(*intermediate_label_);
    }
    // If backward direction specified or forward direction not traversed
    else {
      // Backward
      best_label_ =
          std::make_shared<labelling::Label>(labelling::processBwdLabel(
              *intermediate_label_, max_res, min_res, true));
    }
  }
}

double BiDirectional::getUB() {
  double      UB       = INF;
  const auto& fwd_best = fwd_search_->best_labels[graph->sink.idx];
  const auto& bwd_best = bwd_search_->best_labels[graph->source.idx];
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
  for (const int& n : fwd_search_->visited_vertices) {
    if (fwd_search_->best_labels[n] &&
        fwd_search_->best_labels[n]->weight < *fwd_min) {
      *fwd_min = fwd_search_->best_labels[n]->weight;
    }
  }
  // backward
  *bwd_min = INF;
  for (const int& n : bwd_search_->visited_vertices) {
    if (bwd_search_->best_labels[n] &&
        bwd_search_->best_labels[n]->weight < *bwd_min) {
      *bwd_min = bwd_search_->best_labels[n]->weight;
    }
  }
}

void BiDirectional::joinLabels() {
  // one can sort the labels prior to joining but it takes too long
  // fwd_search_->cleanUp();
  // bwd_search_->cleanUp();
  // upper bound on source-sink path
  double        UB      = getUB();
  const double& HF      = fwd_search_->getHalfWayPoint();
  auto          fwd_min = std::make_unique<double>();
  auto          bwd_min = std::make_unique<double>();
  // lower bounds on forward and backward labels
  getMinimumWeights(fwd_min.get(), bwd_min.get());
  for (const int& n : fwd_search_->visited_vertices) {
    // for each vertex visited forward
    if (fwd_search_->best_labels[n]->weight + *bwd_min <= UB &&
        n != graph->sink.idx) {
      // if bound check fwd_label
      for (auto fwd_iter = fwd_search_->efficient_labels[n].cbegin();
           fwd_iter != fwd_search_->efficient_labels[n].cend();
           ++fwd_iter) { // for each forward label at n
        const labelling::Label& fwd_label = *fwd_iter;
        if (fwd_label.resource_consumption[0] <= HF &&
            fwd_label.weight + *bwd_min <= UB) { // if bound check fwd_label
          const std::vector<AdjVertex>& adj_vertices = graph->adjacency_list[n];
          for (std::vector<AdjVertex>::const_iterator it =
                   adj_vertices.cbegin();
               it != adj_vertices.cend();
               ++it) { // for each successors of n
            // get successors idx (m)
            const int&    m           = (*it).vertex.idx;
            const double& edge_weight = (*it).weight;
            if (bwd_search_->checkVertexVisited(m) && m != graph->source.idx &&
                (fwd_label.weight + edge_weight +
                     bwd_search_->best_labels[m]->weight <=
                 UB)) {
              for (auto bwd_iter = bwd_search_->efficient_labels[m].cbegin();
                   bwd_iter != bwd_search_->efficient_labels[m].cend();
                   ++bwd_iter) { // for each backward label at m
                const labelling::Label& bwd_label = *bwd_iter;
                if (bwd_label.resource_consumption[0] > HF &&
                    (fwd_label.weight + edge_weight + bwd_label.weight <= UB) &&
                    labelling::mergePreCheck(
                        fwd_label, bwd_label, max_res, elementary)) {
                  const labelling::Label merged_label = labelling::mergeLabels(
                      fwd_label,
                      bwd_label,
                      *label_extension_,
                      *graph,
                      max_res,
                      min_res);
                  if (!merged_label.vertex.id.empty() &&
                      merged_label.checkFeasibility(max_res, min_res)) {
                    if (best_label_->vertex.id.empty() ||
                        (merged_label.fullDominance(
                             *best_label_, "forward", elementary) ||
                         merged_label.weight < best_label_->weight)) {
                      // Save
                      best_label_ =
                          std::make_shared<labelling::Label>(merged_label);
                      // Tighten UB
                      if (best_label_->weight < UB) {
                        UB = best_label_->weight;
                      }
                      // Stop if time out or threshold found
                      if (terminate(*best_label_)) {
                        return;
                      }
                    }
                  }
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
