#include "labelling.h"

#include <algorithm> // sort, includes, copy_if, find, push/make_heap, adj_vertex
#include <iostream>  // ostream

namespace labelling {

/**
 * Label
 */

/* Constructors */

Label::Label(
    const double&                weight_in,
    const bidirectional::Vertex& vertex_in,
    const std::vector<double>&   resource_consumption_in,
    const std::vector<int>&      partial_path_in,
    bidirectional::Params*       params_ptr_in)
    : weight(weight_in),
      vertex(vertex_in),
      resource_consumption(resource_consumption_in),
      partial_path(partial_path_in),
      params_ptr(params_ptr_in) {
  if (params_ptr->elementary) {
    unreachable_nodes = partial_path;
    std::sort(unreachable_nodes.begin(), unreachable_nodes.end());
  }
};

// Label::Label(
//     const double&                weight_in,
//     const bidirectional::Vertex& vertex_in,
//     const std::vector<double>&   resource_consumption_in,
//     const std::vector<int>&      partial_path_in,
//     const bidirectional::Params& params)
//     : Label(
//           weight_in,
//           vertex_in,
//           resource_consumption_in,
//           partial_path_in,
//           params.elementary,
//           params.critical_res) {}

Label::Label(
    const double&                weight_in,
    const bidirectional::Vertex& vertex_in,
    const std::vector<double>&   resource_consumption_in,
    const std::vector<int>&      partial_path_in,
    bidirectional::Params*       params_ptr_in,
    const double&                phi_in)
    : Label(
          weight_in,
          vertex_in,
          resource_consumption_in,
          partial_path_in,
          params_ptr_in) {
  setPhi(phi_in);
}

/* Public methods */

Label Label::extend(
    const bidirectional::AdjVertex&  adjacent_vertex,
    const bidirectional::Directions& direction,
    const std::vector<double>&       max_res,
    const std::vector<double>&       min_res) {
  // extract partial_path
  auto new_partial_path = partial_path;
  // extract vertex
  const bidirectional::Vertex& new_node = adjacent_vertex.vertex;
  // update partial_path
  new_partial_path.push_back(new_node.user_id);
  // Propagate resources
  std::vector<double> new_resources;
  if (direction == bidirectional::FWD) {
    if (params_ptr->ref_callback == nullptr) {
      new_resources = bidirectional::additiveForwardREF(
          resource_consumption, adjacent_vertex.resource_consumption);
    } else {
      new_resources = params_ptr->ref_callback->REF_fwd(
          resource_consumption,
          vertex.user_id,
          new_node.user_id,
          adjacent_vertex.resource_consumption,
          partial_path,
          weight);
    }
  } else {
    // backward
    if (params_ptr->ref_callback == nullptr) {
      new_resources = bidirectional::additiveBackwardREF(
          resource_consumption,
          adjacent_vertex.resource_consumption,
          params_ptr->critical_res);
    } else {
      new_resources = params_ptr->ref_callback->REF_bwd(
          resource_consumption,
          new_node.user_id,
          vertex.user_id,
          adjacent_vertex.resource_consumption,
          partial_path,
          weight);
    }
  }
  // Check feasibility before creating
  Label new_label(
      weight + adjacent_vertex.weight,
      new_node,
      new_resources,
      new_partial_path,
      params_ptr);
  if (new_label.checkFeasibility(max_res, min_res)) {
    return new_label;
  } else {
    // Update current labels unreachable_nodes
    if (params_ptr->elementary) {
      // Push new node (direction doesn't matter here as edges have been
      // reversed for backward extensions)
      unreachable_nodes.push_back(new_node.user_id);
      // Keep them sorted for comparison
      std::sort(unreachable_nodes.begin(), unreachable_nodes.end());
    }
  }
  return Label();
}

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
  if (weight <= threshold)
    return true;
  return false;
}

bool Label::checkStPath(const int& source_id, const int& sink_id) const {
  if ((partial_path[0] == source_id && partial_path.back() == sink_id) ||
      (partial_path.back() == source_id && partial_path[0] == sink_id))
    return true;
  return false;
}

bool Label::checkDominance(
    const Label&                     other,
    const bidirectional::Directions& direction) const {
  const int& resource_size = resource_consumption.size();
  const int& c_res         = params_ptr->critical_res;

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
  if (direction == bidirectional::BWD) {
    // Compare monotone resources
    if (resource_consumption[c_res] < other.resource_consumption[c_res]) {
      return false;
    }
    // Compare the rest
    for (int i = 0; i < resource_size; i++) {
      // Exclude critical_res
      if (i != c_res) {
        if (resource_consumption[i] > other.resource_consumption[i]) {
          return false;
        }
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
  if (params_ptr->elementary && unreachable_nodes.size() > 0 &&
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
    const Label&                     other,
    const bidirectional::Directions& direction) const {
  const bool& this_dominates  = checkDominance(other, direction);
  const bool& other_dominates = checkDominance(other, direction);

  if (this_dominates)
    return true;

  bool result = false;
  if (!this_dominates && !other_dominates) {
    bidirectional::Directions flipped_direction;
    if (direction == bidirectional::FWD)
      flipped_direction = bidirectional::BWD;
    else
      flipped_direction = bidirectional::FWD;
    const bool& this_dominates_flipped =
        checkDominance(other, flipped_direction);
    if (this_dominates_flipped || weight < other.weight)
      result = true;
  }
  return result;
}

/* Operator Overloads */

bool operator==(const Label& label1, const Label& label2) {
  if (label1.vertex.lemon_id != label2.vertex.lemon_id)
    return false;
  if (label1.weight != label2.weight)
    return false;
  if (label1.partial_path != label2.partial_path)
    return false;
  /// Check every resource for inequality
  for (int i = 0; i < label1.resource_consumption.size(); i++) {
    if (label1.resource_consumption[i] != label2.resource_consumption[i]) {
      return false;
    }
  }
  return true;
}

bool operator<(const Label& label1, const Label& label2) {
  const int& c_res = label1.params_ptr->critical_res;
  return (
      label1.resource_consumption[c_res] < label2.resource_consumption[c_res]);
}

bool operator>(const Label& label1, const Label& label2) {
  const int& c_res = label1.params_ptr->critical_res;
  return (
      label1.resource_consumption[c_res] > label2.resource_consumption[c_res]);
}

std::ostream& operator<<(std::ostream& os, const Label& label) {
  const int& c_res = label.params_ptr->critical_res;
  os << "Label(node=" << label.vertex.user_id << ", weight= " << label.weight
     << ", res[" << c_res << "]=" << label.resource_consumption[c_res]
     << ", partial_path=[";
  for (auto n : label.partial_path)
    os << n << ",";
  os << "])\n";
  return os;
}

/**
 * Misc functionality
 */

bool runDominanceEff(
    std::vector<Label>*              efficient_labels_ptr,
    const Label&                     label,
    const bidirectional::Directions& direction,
    const bool&                      elementary) {
  bool dominated = false;
  for (auto it = efficient_labels_ptr->begin();
       it != efficient_labels_ptr->end();) {
    bool         deleted = false;
    const Label& label2  = *it;
    if (label != label2) {
      // check if label dominates label2
      if (label.checkDominance(label2, direction)) {
        // Delete label2
        it      = efficient_labels_ptr->erase(it);
        deleted = true;
      } else if (label2.checkDominance(label, direction)) {
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
    std::vector<Label>*              labels_ptr,
    const bidirectional::Directions& direction) {
  if (direction == bidirectional::FWD)
    std::pop_heap(labels_ptr->begin(), labels_ptr->end(), std::greater<>{});
  else
    std::pop_heap(labels_ptr->begin(), labels_ptr->end());

  // Get next label as the back of the heap
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
  std::vector<int> new_path = label.partial_path;
  std::reverse(new_path.begin(), new_path.end());
  // Init resources
  std::vector<double> new_resources(label.resource_consumption);
  // Invert monotone resource
  const int& c_res     = label.params_ptr->critical_res;
  new_resources[c_res] = max_res[c_res] - new_resources[c_res];

  if (!invert_min_res) {
    // Elementwise cumulative_resource + new_resources
    std::transform(
        new_resources.begin(),
        new_resources.end(),
        cumulative_resource.begin(),
        new_resources.begin(),
        std::plus<double>());
  }
  return Label(
      label.weight, label.vertex, new_resources, new_path, label.params_ptr);
}

double getPhiValue(
    const labelling::Label&    fwd_label,
    const labelling::Label&    bwd_label,
    const std::vector<double>& max_res) {
  const int& id = fwd_label.params_ptr->critical_res;
  return std::abs(
      fwd_label.resource_consumption[id] -
      (max_res[id] - bwd_label.resource_consumption[id]));
}

bool halfwayCheck(const Label& label, const std::vector<Label>& labels) {
  // attempt to find path in already seen labels with lower phi value
  auto it =
      std::find_if(labels.begin(), labels.end(), [&label](const Label& l) {
        // If path already seen
        if (std::equal(
                l.partial_path.begin(),
                l.partial_path.end(),
                label.partial_path.begin())) {
          // Match if phi value is lower
          return (l.phi < label.phi);
        }
        return false;
      });
  // Path already been found with lower phi value
  if (it != labels.end())
    return false;
  // Path not been found or phi value is lower
  return true;
}

bool mergePreCheck(
    const labelling::Label&   fwd_label,
    const labelling::Label&   bwd_label,
    const std::vector<double> max_res) {
  bool result = true;
  if (fwd_label.vertex.lemon_id == -1 || bwd_label.vertex.lemon_id == -1)
    return false;
  if (fwd_label.params_ptr->elementary) {
    std::vector<int> path_copy = fwd_label.partial_path;
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
    const Label&                    fwd_label,
    const Label&                    bwd_label,
    const bidirectional::AdjVertex& adj_vertex,
    const bidirectional::Vertex&    sink,
    const std::vector<double>&      max_res,
    const std::vector<double>&      min_res) {
  // No edge between the labels return empty label
  if (!adj_vertex.init) {
    return Label();
  }
  std::vector<double>    final_res;
  bidirectional::Params* params_ptr = fwd_label.params_ptr;
  // Dummy label
  auto bwd_label_ptr = std::make_unique<Label>();
  // Extend resources along edge
  if (params_ptr->ref_callback == nullptr) {
    const std::vector<double>& temp_res = bidirectional::additiveForwardREF(
        fwd_label.resource_consumption, adj_vertex.resource_consumption);
    // Process backward label (invert path and resources)
    auto bwd_label_ =
        std::make_unique<Label>(processBwdLabel(bwd_label, max_res, temp_res));
    final_res = bwd_label_->resource_consumption;
    bwd_label_ptr.swap(bwd_label_);
  } else {
    final_res = params_ptr->ref_callback->REF_join(
        fwd_label.resource_consumption,
        bwd_label.resource_consumption,
        fwd_label.vertex.user_id,
        bwd_label.vertex.user_id,
        adj_vertex.resource_consumption);
    // Invert backward resource
    const int&   c_res = params_ptr->critical_res;
    const double bwd_res_inverted =
        max_res[c_res] - bwd_label.resource_consumption[c_res];
    // in the case when default REF_join has been called (or user hasn't
    // added resource consumption)
    const double& bwd_monotone_edge =
        (adj_vertex.resource_consumption[c_res] == 0)
            ? 1
            : adj_vertex.resource_consumption[c_res];
    if (final_res[c_res] != (fwd_label.resource_consumption[c_res] +
                             bwd_monotone_edge + bwd_res_inverted)) {
      final_res[c_res] += bwd_res_inverted;
    }
    auto bwd_label_ =
        std::make_unique<Label>(processBwdLabel(bwd_label, max_res, min_res));
    bwd_label_ptr.swap(bwd_label_);
  }
  // process final weight
  const double& weight =
      fwd_label.weight + adj_vertex.weight + bwd_label_ptr->weight;
  // Process final path
  std::vector<int> final_path = fwd_label.partial_path;
  final_path.insert(
      final_path.end(),
      bwd_label_ptr->partial_path.begin(),
      bwd_label_ptr->partial_path.end());
  // Get phi value
  const double& phi = getPhiValue(fwd_label, bwd_label, max_res);
  return Label(weight, sink, final_res, final_path, params_ptr, phi);
}

} // namespace labelling
