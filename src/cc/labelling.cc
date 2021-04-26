#include "labelling.h"

#include <algorithm> // sort, includes, copy_if, find, push/make_heap, adj_vertex
#include <iostream>  // ostream
#include <set>

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
  const int& resource_size = resource_consumption.size();
  for (int i = 0; i < resource_size; i++) {
    if (resource_consumption[i] <= max_res[i] &&
        resource_consumption[i] >= min_res[i]) {
      ;
    } else {
      return false;
    }
  }
  return true;
}

bool Label::checkThreshold(const double& threshold) const {
  if (weight <= threshold) {
    return true;
  }
  return false;
}

bool Label::checkStPath() const {
  if ((partial_path[0] == "Source" && partial_path.back() == "Sink") ||
      (partial_path.back() == "Source" && partial_path[0] == "Sink")) {
    return true;
  }
  return false;
}

bool Label::checkDominance(
    const Label&       other,
    const std::string& direction,
    const bool&        elementary) const {
  const int& resource_size = resource_consumption.size();

  if (weight == other.weight) {
    // Check if all resources are equal
    bool all_res_equal = true;
    for (int i = 0; i < resource_size; i++) {
      if (resource_consumption[i] != other.resource_consumption[i]) {
        all_res_equal = false;
      }
    }
    if (all_res_equal) {
      return false;
    }
  }
  // Compare weight
  if (weight > other.weight) {
    return false;
  }
  if (direction == "backward") {
    // Compare monotone resources
    if (resource_consumption[0] < other.resource_consumption[0]) {
      return false;
    }
    // Compare the rest
    for (int i = 1; i < resource_size; i++) {
      if (resource_consumption[i] > other.resource_consumption[i]) {
        return false;
      }
    }
  } else { // Forward
    for (int i = 0; i < resource_size; i++) {
      if (resource_consumption[i] > other.resource_consumption[i]) {
        return false;
      }
    }
  }
  // Check for the elementary case
  if (elementary && unreachable_nodes.size() > 0 &&
      other.unreachable_nodes.size() > 0) {
    if (std::includes(
            unreachable_nodes.begin(),
            unreachable_nodes.end(),
            other.unreachable_nodes.begin(),
            other.unreachable_nodes.end())) {
      // If the unreachable_nodes are the same, this leads to one equivalent
      // label to be removed
      if (unreachable_nodes == other.unreachable_nodes) {
        return true;
      }
      return false;
    }
  }
  // this dominates other
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

/* Operator Overloads */

bool operator<(const Label& label1, const Label& label2) {
  return (label1.resource_consumption[0] < label2.resource_consumption[0]);
}

bool operator>(const Label& label1, const Label& label2) {
  return (label1.resource_consumption[0] > label2.resource_consumption[0]);
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
  ref_callback = nullptr;
  delete ref_callback;
}

void LabelExtension::setREFCallback(bidirectional::REFCallback* cb) {
  ref_callback = cb;
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
    if (ref_callback == nullptr) {
      new_resources = bidirectional::additiveForwardREF(
          label->resource_consumption,
          label->vertex.id,
          new_node.id,
          adjacent_vertex.resource_consumption);
    } else {
      new_resources = ref_callback->REF_fwd(
          label->resource_consumption,
          label->vertex.id,
          new_node.id,
          adjacent_vertex.resource_consumption,
          label->partial_path,
          label->weight);
    }
  } else {
    // backward
    if (ref_callback == nullptr) {
      new_resources = bidirectional::additiveBackwardREF(
          label->resource_consumption,
          new_node.id,
          label->vertex.id,
          adjacent_vertex.resource_consumption);
    } else {
      new_resources = ref_callback->REF_bwd(
          label->resource_consumption,
          new_node.id,
          label->vertex.id,
          adjacent_vertex.resource_consumption,
          label->partial_path,
          label->weight);
    }
  }
  // Check feasibility before creating
  Label new_label(
      label->weight + adjacent_vertex.weight,
      new_node,
      new_resources,
      new_partial_path,
      elementary);
  if (new_label.checkFeasibility(max_res, min_res)) {
    return new_label;
  } else {
    // Update current labels unreachable_nodes
    if (elementary) {
      // Push new node (direction doesn't matter here as edges have been
      // reversed for backward extensions)
      label->unreachable_nodes.push_back(new_node.id);
      // Keep them sorted for comparison
      std::sort(
          label->unreachable_nodes.begin(), label->unreachable_nodes.end());
    }
  }
  return Label();
}

/**
 * Misc
 */

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
      // check if label1 dominates label2 and remove if it is resource feasible
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
  // Init resources
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
  if (invert_min_res) {
    // invert minimum resource from original resources and place in
    // new_resources
    std::transform(
        new_resources.cbegin() + 1,
        new_resources.cend(),
        cumulative_resource.begin() + 1,
        new_resources.begin() + 1,
        std::minus<double>());
  }
  return Label(label.weight, label.vertex, new_resources, new_path);
}

double getPhiValue(
    const labelling::Label&    fwd_label,
    const labelling::Label&    bwd_label,
    const std::vector<double>& max_res) {
  return std::abs(
      fwd_label.resource_consumption[0] -
      (max_res[0] - bwd_label.resource_consumption[0]));
}

bool halfwayCheck(
    const std::vector<std::pair<double, std::vector<std::string>>>& st_paths,
    const std::pair<double, std::vector<std::string>>& phi_path_pair) {
  // attempt to find path is st_paths with lower phi
  auto it = std::find_if(
      st_paths.begin(),
      st_paths.end(),
      [&phi_path_pair](
          const std::pair<double, std::vector<std::string>>& elem) {
        // If path already seen
        if (std::equal(
                elem.second.begin(),
                elem.second.end(),
                phi_path_pair.second.begin())) {
          // Match if phi value is lower
          return (elem.first < phi_path_pair.first);
        }
        return false;
      });
  // Path already been found with lower phi value
  if (it != st_paths.end()) {
    return false;
  }
  // Path not been found or phi value is lower
  return true;
}

bool mergePreCheck(
    const labelling::Label&   fwd_label,
    const labelling::Label&   bwd_label,
    const std::vector<double> max_res,
    const bool&               elementary) {
  bool result = true;
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
    result = !contains_duplicates;
  }
  return result;
}

Label mergeLabels(
    const Label&                  fwd_label,
    const Label&                  bwd_label,
    const LabelExtension&         label_extension_,
    const bidirectional::DiGraph& graph,
    const std::vector<double>&    max_res,
    const std::vector<double>&    min_res) {
  const bidirectional::AdjVertex& adj_vertex =
      graph.getAdjVertex(fwd_label.vertex.idx, bwd_label.vertex.idx);
  // No edge between the labels return empty label
  if (!adj_vertex.init) {
    return Label();
  }
  std::vector<double> final_res;
  auto                bwd_label_ptr = std::make_unique<Label>();
  // Extend resources along edge
  if (label_extension_.ref_callback == nullptr) {
    const std::vector<double>& temp_res = bidirectional::additiveForwardREF(
        fwd_label.resource_consumption,
        fwd_label.vertex.id,
        bwd_label.vertex.id,
        adj_vertex.resource_consumption);
    // Process backward label (invert path and resources)
    auto bwd_label_ =
        std::make_unique<Label>(processBwdLabel(bwd_label, max_res, temp_res));
    final_res = bwd_label_->resource_consumption;
    bwd_label_ptr.swap(bwd_label_);
  } else {
    final_res = label_extension_.ref_callback->REF_join(
        fwd_label.resource_consumption,
        bwd_label.resource_consumption,
        fwd_label.vertex.id,
        bwd_label.vertex.id,
        adj_vertex.resource_consumption);
    const double bwd_res_inverted =
        max_res[0] - bwd_label.resource_consumption[0];
    // in the case when default REF_join has been called (or user hasn't added
    // resource consumption)
    const double& bwd_monotone_edge = (adj_vertex.resource_consumption[0] == 0)
                                          ? 1
                                          : adj_vertex.resource_consumption[0];
    if (final_res[0] != (fwd_label.resource_consumption[0] + bwd_monotone_edge +
                         bwd_res_inverted)) {
      final_res[0] += bwd_res_inverted;
    }
    auto bwd_label_ =
        std::make_unique<Label>(processBwdLabel(bwd_label, max_res, min_res));
    bwd_label_ptr.swap(bwd_label_);
  }
  const double& weight =
      fwd_label.weight + adj_vertex.weight + bwd_label_ptr->weight;
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
    // Min-heap
    std::make_heap(labels_ptr->begin(), labels_ptr->end(), std::greater<>{});
  } else {
    // Max-heap
    std::make_heap(labels_ptr->begin(), labels_ptr->end());
  }
}

void pushHeap(
    std::vector<labelling::Label>* labels_ptr,
    const std::string&             direction) {
  if (labels_ptr->size() > 1) {
    if (direction == "forward") {
      // Min-heap
      std::push_heap(labels_ptr->begin(), labels_ptr->end(), std::greater<>{});
    } else {
      // Max-heap
      std::push_heap(labels_ptr->begin(), labels_ptr->end());
    }
  }
}

} // namespace labelling
