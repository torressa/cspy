#include "ref_callback.h"

#include <algorithm> // transform

namespace bidirectional {

std::vector<double> additiveForwardREF(
    const std::vector<double>& cumulative_resource,
    const std::string&         tail,
    const std::string&         head,
    const std::vector<double>& edge_resource_consumption) {
  // Add element wise
  std::vector<double> new_resources = cumulative_resource;
  std::transform(
      new_resources.begin(),
      new_resources.end(),
      edge_resource_consumption.begin(),
      new_resources.begin(),
      std::plus<double>());
  return new_resources;
}

std::vector<double> additiveBackwardREF(
    const std::vector<double>& cumulative_resource,
    const std::string&         tail,
    const std::string&         head,
    const std::vector<double>& edge_resource_consumption) {
  std::vector<double> new_resources = cumulative_resource;
  std::transform(
      new_resources.begin(),
      new_resources.end(),
      edge_resource_consumption.begin(),
      new_resources.begin(),
      std::plus<double>());
  if (edge_resource_consumption[0] > 0) {
    new_resources[0] = cumulative_resource[0] - edge_resource_consumption[0];
  } else {
    new_resources[0] = cumulative_resource[0] - 1;
  }
  return new_resources;
}

std::vector<double> REFCallback::REF_fwd(
    const std::vector<double>&      cumulative_resource,
    const std::string&              tail,
    const std::string&              head,
    const std::vector<double>&      edge_resource_consumption,
    const std::vector<std::string>& partial_path,
    const double&                   accummulated_cost) const {
  return additiveForwardREF(
      cumulative_resource, tail, head, edge_resource_consumption);
}

std::vector<double> REFCallback::REF_bwd(
    const std::vector<double>&      cumulative_resource,
    const std::string&              tail,
    const std::string&              head,
    const std::vector<double>&      edge_resource_consumption,
    const std::vector<std::string>& partial_path,
    const double&                   accummulated_cost) const {
  return additiveBackwardREF(
      cumulative_resource, tail, head, edge_resource_consumption);
}

std::vector<double> REFCallback::REF_join(
    const std::vector<double>& fwd_resource,
    const std::vector<double>& bwd_resource,
    const std::string&         tail,
    const std::string&         head,
    const std::vector<double>& edge_resource_consumption) const {
  return REF_fwd(fwd_resource, tail, head, edge_resource_consumption, {}, 0.0);
}

} // namespace bidirectional
