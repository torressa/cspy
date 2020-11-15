#include "labelling.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <set>

#include "py_ref_callback.h"

namespace labelling {

/**
 * Label
 */
// constructors
Label::Label(
    const double&                   weight,
    const bidirectional::Vertex&    vertex,
    const std::vector<double>&      resource_consumption,
    const std::vector<std::string>& partial_path,
    const bool&                     elementary)
    : weight(weight),
      vertex(vertex),
      resource_consumption(resource_consumption),
      partial_path(partial_path) {
  if (elementary) {
    unreachable_nodes = partial_path;
    std::sort(unreachable_nodes.begin(), unreachable_nodes.end());
  }
};

bool Label::checkFeasibility(
    const std::vector<double>& max_res,
    const std::vector<double>& min_res) const {
  if (resource_consumption <= max_res && resource_consumption >= min_res)
    return true;
  return false;
}

bool Label::checkThreshold(const double& threshold) const {
  if (weight <= threshold)
    return true;
  return false;
}

bool Label::checkStPath() const {
  if ((partial_path[0] == "Source" && partial_path.back() == "Sink") ||
      (partial_path.back() == "Source" && partial_path[0] == "Sink"))
    return true;
  return false;
}

bool Label::checkDominance(
    const Label&       other,
    const std::string& direction,
    const bool&        elementary) const {
  if (weight == other.weight &&
      resource_consumption == other.resource_consumption)
    return false;
  // Compare weight
  if (weight > other.weight)
    return false;
  const int& resource_size = resource_consumption.size();
  if (direction == "backward") {
    // Compare monotone resources
    if (resource_consumption[0] < other.resource_consumption[0])
      return false;
    // Compare the rest
    for (int i = 1; i < resource_size; i++) {
      if (resource_consumption[i] > other.resource_consumption[i])
        return false;
    }
  } else { // Forward
    for (int i = 0; i < resource_size; i++) {
      if (resource_consumption[i] > other.resource_consumption[i])
        return false;
    }
  }
  if (elementary && unreachable_nodes.size() > 0 &&
      other.unreachable_nodes.size() > 0) {
    if (std::includes(
            unreachable_nodes.begin(),
            unreachable_nodes.end(),
            other.unreachable_nodes.begin(),
            other.unreachable_nodes.end())) {
      // If the unreachable_nodes are the same, this leads to one equivalent
      // label to be removed
      if (unreachable_nodes == other.unreachable_nodes)
        return true;
      else
        return false;
    }
  }
  return true;
}

bool Label::fullDominance(
    const Label&       other,
    const std::string& direction,
    const bool&        elementary) const {
  const bool& this_dominates  = checkDominance(other, direction, elementary);
  const bool& other_dominates = checkDominance(other, direction, elementary);

  if (this_dominates)
    return true;

  bool result = false;
  if (!this_dominates && !other_dominates) {
    std::string flipped_direction;
    if (direction == "forward")
      flipped_direction = "backward";
    else
      flipped_direction = "forward";
    const bool& this_dominates_flipped =
        checkDominance(other, flipped_direction, elementary);
    if (this_dominates_flipped || weight < other.weight)
      result = true;
  }
  return result;
}

// operator overloads
bool operator<(const Label& label1, const Label& label2) {
  return (label1.resource_consumption[0] < label2.resource_consumption[0]);
}

std::ostream& operator<<(std::ostream& os, const Label& label) {
  os << "Label(node=" << label.vertex.id << ", weight= " << label.weight
     << ", res[0]=" << label.resource_consumption[0] << ", partial_path=[";
  for (auto n : label.partial_path)
    os << "'" << n << "', ";
  os << "])\n";
  return os;
}

bool operator==(const Label& label1, const Label& label2) {
  if (label1.vertex.idx != label2.vertex.idx)
    return false;
  if (label1.weight != label2.weight)
    return false;
  if (label1.partial_path != label2.partial_path)
    return false;
  if (label1.resource_consumption != label2.resource_consumption)
    return false;
  return true;
}

/**
 * LabelExtension
 */
LabelExtension::LabelExtension() {}
LabelExtension::~LabelExtension() {
  py_callback = nullptr;
  delete py_callback;
}

void LabelExtension::setPyCallback(bidirectional::PyREFCallback* cb) {
  py_callback = cb;
}

Label LabelExtension::extend(
    Label*                          label,
    const bidirectional::AdjVertex& adjacent_vertex,
    const std::string&              direction,
    const bool&                     elementary,
    const std::vector<double>&      max_res,
    const std::vector<double>&      min_res) const {
  // extract partial_path
  auto new_partial_path = label->partial_path;
  // extract vertex
  const bidirectional::Vertex& new_node = adjacent_vertex.vertex;
  // update partial_path
  new_partial_path.push_back(new_node.id);
  // Propagate resources
  std::vector<double> new_resources;
  if (direction == "forward") {
    if (py_callback == nullptr) {
      new_resources = bidirectional::additiveForwardREF(
          label->resource_consumption,
          label->vertex.id,
          new_node.id,
          adjacent_vertex.resource_consumption);
    } else {
      new_resources = py_callback->REF_fwd(
          label->resource_consumption,
          label->vertex.id,
          new_node.id,
          adjacent_vertex.resource_consumption,
          label->partial_path,
          label->weight);
    }
  } else {
    // backward
    if (py_callback == nullptr) {
      new_resources = bidirectional::additiveBackwardREF(
          label->resource_consumption,
          new_node.id,
          label->vertex.id,
          adjacent_vertex.resource_consumption);
    } else {
      new_resources = py_callback->REF_bwd(
          label->resource_consumption,
          new_node.id,
          label->vertex.id,
          adjacent_vertex.resource_consumption,
          label->partial_path,
          label->weight);
    }
  }
  // Check feasibility before creating
  if (new_resources <= max_res && new_resources >= min_res) {
    return Label(
        label->weight + adjacent_vertex.weight,
        new_node,
        new_resources,
        new_partial_path,
        elementary);
  } else {
    // Update current labels unreachable_nodes
    if (elementary) {
      label->unreachable_nodes.push_back(new_node.id);
      std::sort(
          label->unreachable_nodes.begin(), label->unreachable_nodes.end());
    }
  }
  return Label();
}

/**
 * Misc
 */

// TODO Clean this mess
//
// void runDominance(
//    std::vector<Label>* unprocessed_labels_ptr,
//    bool*               updated_labels,
//    bool*               updated_best,
//    const Label&        label,
//    const std::string&  direction,
//    const bool&         elementary,
//    const bool&         save) {
//  // for (auto it = labels_ptr->begin(); it != labels_ptr->end();) {
//  //   const Label& label1        = *it;
//  bool non_dominated = true;
//  // Extract labels with the same node
//  // std::vector<Label> comparable_labels(labels_ptr->size());
//  // For each comparable label
//  for (auto it = efficient_labels_ptr->begin();
//       it != efficient_labels_ptr->end();) {
//    bool         deleted = false;
//    const Label& label2  = *it;
//    if (label2 != label) {
//      // check if label1 dominates label2
//      if (label.checkDominance(label2, direction, elementary)) {
//        // const auto& dist =
//        //     std::find(labels_ptr->begin(), labels_ptr->end(), label2);
//        it      = efficient_labels_ptr->erase(it);
//        deleted = true;
//        // *updated_labels = true;
//      } else if (label2.checkDominance(label, direction, elementary)) {
//        // it              = labels_ptr->erase(it);
//        // *updated_labels = true;
//        non_dominated = false;
//        // updateEfficientLabels(label2);
//        break;
//      }
//    }
//    if (!deleted)
//      ++it;
//  }
//  // if (save && non_dominated) {
//  //   *updated_best = true;
//  //   best_labels_ptr->push_back(label);
//  // }
//  // }
//}

bool runDominance(
    std::vector<Label>*                    labels_ptr,
    const std::string&                     direction,
    const bool&                            elementary,
    const std::vector<std::vector<Label>>& efficient_labels) {
  bool updated_labels = false;
  for (auto it = labels_ptr->begin(); it != labels_ptr->end();) {
    const Label& label1  = *it;
    bool         deleted = false;
    // Extract labels with the same node
    std::vector<Label> comparable_labels(
        labels_ptr->begin(), labels_ptr->end());
    auto copy_if_iterator = std::copy_if(
        labels_ptr->begin(),
        labels_ptr->end(),
        comparable_labels.begin(),
        [&label1](const Label& l) {
          return (l.vertex.idx == label1.vertex.idx && l != label1);
        });
    comparable_labels.erase(copy_if_iterator, comparable_labels.end());
    std::set<labelling::Label> setss(
        comparable_labels.begin(), comparable_labels.end());
    setss.insert(
        efficient_labels[label1.vertex.idx].begin(),
        efficient_labels[label1.vertex.idx].end());

    // For each comparable label
    for (auto it2 = comparable_labels.begin(); it2 != comparable_labels.end();
         ++it2) {
      const Label& label2 = *it2;
      // check if label1 dominates label2
      if (label1.checkDominance(label2, direction, elementary)) {
        // find and remove label2
        const auto& dist =
            std::find(labels_ptr->begin(), labels_ptr->end(), label2);
        labels_ptr->erase(dist);
        updated_labels = true;
      } else if (label2.checkDominance(label1, direction, elementary)) {
        // remove label1
        it             = labels_ptr->erase(it);
        updated_labels = true;
        deleted        = true;
        break;
      }
    }
    if (!deleted)
      ++it;
  }
  return updated_labels;
}

bool runDominanceEff(
    std::vector<Label>* efficient_labels_ptr,
    const Label&        label,
    const std::string&  direction,
    const bool&         elementary) {
  bool dominated = false;
  for (auto it = efficient_labels_ptr->begin();
       it != efficient_labels_ptr->end();) {
    bool         deleted = false;
    const Label& label2  = *it;
    if (label != label2) {
      // check if label1 dominates label2
      if (label.checkDominance(label2, direction, elementary)) {
        it      = efficient_labels_ptr->erase(it);
        deleted = true;
      } else if (label2.checkDominance(label, direction, elementary)) {
        dominated = true;
        break;
      }
    }
    if (!deleted)
      ++it;
  }
  return dominated;
}

Label getNextLabel(
    std::vector<Label>* labels_ptr,
    const std::string&  direction) {
  if (direction == "forward")
    std::pop_heap(labels_ptr->begin(), labels_ptr->end(), std::greater<>{});
  else
    std::pop_heap(labels_ptr->begin(), labels_ptr->end());

  Label next_label = labels_ptr->back();
  labels_ptr->pop_back();
  return next_label;
}

Label processBwdLabel(
    const labelling::Label&    label,
    const std::vector<double>& max_res,
    const std::vector<double>& cumulative_resource,
    const bool&                invert_min_res) {
  // Invert path
  std::vector<std::string> new_path = label.partial_path;
  std::reverse(new_path.begin(), new_path.end());
  std::vector<double> new_resources(label.resource_consumption);
  // Invert monotone resource
  new_resources[0] = max_res[0] - new_resources[0];
  // Elementwise cumulative_resource + new_resources
  std::transform(
      new_resources.begin(),
      new_resources.end(),
      cumulative_resource.begin(),
      new_resources.begin(),
      std::plus<double>());
  if (invert_min_res)
    // invert minimum resource
    std::transform(
        ++label.resource_consumption.begin(),
        label.resource_consumption.end(),
        ++cumulative_resource.begin(),
        ++new_resources.begin(),
        std::minus<double>());
  // Invert monotone resource
  return Label(label.weight, label.vertex, new_resources, new_path);
}

bool halfwayCheck(
    const labelling::Label&   fwd_label,
    const labelling::Label&   bwd_label,
    const std::vector<double> max_res) {
  const double phi = std::abs(
      fwd_label.resource_consumption[0] -
      (max_res[0] - bwd_label.resource_consumption[0]));
  return ((0.0 <= phi) && (phi <= 2.0));
}

bool mergePreCheck(
    const labelling::Label&   fwd_label,
    const labelling::Label&   bwd_label,
    const std::vector<double> max_res,
    const bool&               elementary) {
  if (fwd_label.vertex.id.empty() || bwd_label.vertex.id.empty())
    return false;
  if (elementary) {
    std::vector<std::string> path_copy = fwd_label.partial_path;
    path_copy.insert(
        path_copy.end(),
        bwd_label.partial_path.begin(),
        bwd_label.partial_path.end());
    std::sort(path_copy.begin(), path_copy.end());
    const bool& contains_duplicates =
        std::adjacent_find(path_copy.begin(), path_copy.end()) !=
        path_copy.end();
    return !contains_duplicates;
  }
  return halfwayCheck(fwd_label, bwd_label, max_res);
}

Label mergeLabels(
    const Label&                  fwd_label,
    const Label&                  bwd_label,
    const LabelExtension&         label_extension_,
    const bidirectional::DiGraph& graph,
    const std::vector<double>&    max_res,
    const std::vector<double>&    min_res) {
  bidirectional::AdjVertex adj_vertex =
      graph.getAdjVertex(fwd_label.vertex.idx, bwd_label.vertex.idx);
  // No edge between the labels return empty label
  if (!adj_vertex.init) {
    return Label();
  }
  std::vector<double> final_res;
  auto                bwd_label_ptr = std::make_unique<Label>();
  if (label_extension_.py_callback == nullptr) {
    std::vector<double> temp_res = bidirectional::additiveForwardREF(
        fwd_label.resource_consumption,
        fwd_label.vertex.id,
        bwd_label.vertex.id,
        adj_vertex.resource_consumption);
    auto bwd_label_ =
        std::make_unique<Label>(processBwdLabel(bwd_label, max_res, temp_res));
    final_res = bwd_label_->resource_consumption;
    bwd_label_ptr.swap(bwd_label_);
  } else {
    final_res = label_extension_.py_callback->REF_join(
        fwd_label.resource_consumption,
        bwd_label.resource_consumption,
        fwd_label.vertex.id,
        bwd_label.vertex.id,
        adj_vertex.resource_consumption);
    auto bwd_label_ =
        std::make_unique<Label>(processBwdLabel(bwd_label, max_res, min_res));
    bwd_label_ptr.swap(bwd_label_);
  }
  double weight = fwd_label.weight + adj_vertex.weight + bwd_label_ptr->weight;
  std::vector<std::string> final_path = fwd_label.partial_path;
  final_path.insert(
      final_path.end(),
      bwd_label_ptr->partial_path.begin(),
      bwd_label_ptr->partial_path.end());
  return Label(weight, graph.sink, final_res, final_path);
}

void makeHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction) {
  if (direction == "forward") {
    std::make_heap(labels_ptr->begin(), labels_ptr->end(), std::greater<>{});
  } else
    std::make_heap(labels_ptr->begin(), labels_ptr->end());
}

void pushHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction) {
  if (labels_ptr->size() > 1) {
    if (direction == "forward") {
      std::push_heap(labels_ptr->begin(), labels_ptr->end(), std::greater<>{});
    } else
      std::push_heap(labels_ptr->begin(), labels_ptr->end());
  }
}

} // namespace labelling
