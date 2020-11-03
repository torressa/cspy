#include "bidirectional.h"

#include <stdlib.h>

#include <algorithm>
#include <iostream>

namespace bidirectional {

BiDirectional::BiDirectional(
    const std::vector<double>& max_res_in,
    const std::vector<double>& min_res_in)
    : graph(new DiGraph()), max_res(max_res_in), min_res(min_res_in) {
  label_extension_ = std::make_shared<labelling::LabelExtension>();
  labelling::Label label(0.0, "", {}, {});
  best_label = std::make_shared<labelling::Label>(label);
  // setSeed();
}

BiDirectional::~BiDirectional() {}

void BiDirectional::setSeed(const int& seed) {
  std::srand(seed);
}

void BiDirectional::setPyCallback(bidirectional::PyREFCallback* cb) const {
  label_extension_->setPyCallback(cb);
}

std::vector<std::string> BiDirectional::getPath() const {
  return best_label->partial_path;
}

std::vector<double> BiDirectional::getConsumedResources() const {
  return best_label->resource_consumption;
}

double BiDirectional::getTotalCost() const {
  return best_label->weight;
}

void BiDirectional::call() const {
  fwd_search_->call();
  bwd_search_->call();
}

void BiDirectional::addEdge(
    const std::string&         tail,
    const std::string&         head,
    const double&              weight,
    const std::vector<double>& resource_consumption) {
  addEdgeToDiGraph(graph, tail, head, weight, resource_consumption);
}

void BiDirectional::run() {
  start_time = clock();
  initSearches();
  while (!fwd_search_->stop || !bwd_search_->stop) {
    const std::string next_direction = getDirection();
    if (!next_direction.empty()) {
      move(next_direction);
      updateFinalLabel();
    } else {
      break;
    }
    if (terminate())
      break;
  }
  cleanUp();
  postProcessing();
}

/**
 * Private methods
 */
// Initalisations
void BiDirectional::initSearches() {
  fwd_search_ = std::make_unique<Search>(
      graph,
      max_res,
      min_res,
      "forward",
      elementary,
      dominance_frequency,
      *label_extension_,
      (direction == "both"));
  bwd_search_ = std::make_unique<Search>(
      graph,
      max_res,
      min_res,
      "backward",
      elementary,
      dominance_frequency,
      *label_extension_,
      (direction == "both"));
}

std::string BiDirectional::getDirection() const {
  if (direction == "both") {
    if (!fwd_search_->stop && bwd_search_->stop)
      return "forward";
    else if (fwd_search_->stop && !bwd_search_->stop)
      return "backward";
    else if (!fwd_search_->stop && !bwd_search_->stop) {
      if (method == "random") {
        // return a random direction
        const std::vector<std::string> directions = {"forward", "backward"};
        const int                      r          = std::rand() % 2;
        return directions[r];
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
    } else
      ;
  } else {
    // Single direction
    if (direction == "forward" && fwd_search_->stop)
      ;
    else if (direction == "backward" && bwd_search_->stop)
      ;
    else
      return direction;
  }
  return "";
}

void BiDirectional::move(const std::string& direction_) {
  if (direction_ == "forward" && !fwd_search_->stop)
    fwd_search_->move(bwd_search_->max_res_curr);
  else if (direction_ == "backward" && !bwd_search_->stop)
    bwd_search_->move(fwd_search_->min_res_curr);
}

void BiDirectional::updateFinalLabel() {
  if (direction == "forward")
    final_label = std::make_shared<labelling::Label>(*fwd_search_->final_label);
  else if (direction == "backward")
    final_label = std::make_shared<labelling::Label>(*bwd_search_->final_label);
  else {
    if (!fwd_search_->final_label->node.empty())
      final_label =
          std::make_shared<labelling::Label>(*fwd_search_->final_label);
    else if (!bwd_search_->final_label->node.empty())
      final_label =
          std::make_shared<labelling::Label>(*bwd_search_->final_label);
  }
}

bool BiDirectional::terminate() const {
  clock_t timediff     = clock() - start_time;
  double  timediff_sec = ((double)timediff) / CLOCKS_PER_SEC;
  if (!std::isnan(time_limit) && timediff_sec >= time_limit) {
    return true;
  }
  return checkFinalLabel();
}

bool BiDirectional::checkFinalLabel() const {
  if (final_label && final_label->checkStPath()) {
    if (!std::isnan(threshold) && final_label->checkThreshold(threshold)) {
      return true;
    }
  }
  return false;
}

void BiDirectional::cleanUp() const {
  fwd_search_->cleanUp();
  bwd_search_->cleanUp();
}

void BiDirectional::postProcessing() {
  if (direction == "both") {
    // If bidirectional algorithm used, run path joining procedure.
    joinLabels();
  } else {
    // If forward direction specified or backward direction not traversed
    if (direction == "forward")
      // Forward
      best_label = std::make_shared<labelling::Label>(*final_label);
    // If backward direction specified or forward direction not traversed
    else {
      // Backward
      best_label = std::make_shared<labelling::Label>(
          labelling::processBwdLabel(*final_label, max_res, min_res, true));
    }
  }
}

void BiDirectional::joinLabels() {
  for (auto fwd_iter = fwd_search_->best_labels->begin();
       fwd_iter != fwd_search_->best_labels->end();
       fwd_iter++) {
    const labelling::Label& fwd_label = *fwd_iter;
    for (auto bwd_iter = bwd_search_->best_labels->begin();
         bwd_iter != bwd_search_->best_labels->end();
         bwd_iter++) {
      const labelling::Label& bwd_label = *bwd_iter;
      if (checkEdgeInDiGraph(*graph, fwd_label.node, bwd_label.node) &&
          labelling::mergePreCheck(fwd_label, bwd_label, max_res, elementary)) {
        const labelling::Label merged_label = labelling::mergeLabels(
            fwd_label, bwd_label, *label_extension_, *graph, max_res, min_res);
        if (merged_label.checkFeasibility(max_res, min_res)) {
          if (best_label->node.empty() ||
              (merged_label.fullDominance(*best_label, "forward", elementary) ||
               merged_label.weight < best_label->weight)) {
            // Save
            best_label = std::make_shared<labelling::Label>(merged_label);
            if (!std::isnan(threshold) &&
                best_label->checkThreshold(threshold)) {
              return;
            }
          }
        }
      }
    }
  }
}

} // namespace bidirectional
