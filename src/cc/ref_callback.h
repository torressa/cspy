#ifndef BIDIRECTIONAL_REF_CALLBACK_H__
#define BIDIRECTIONAL_REF_CALLBACK_H__

#include <string>
#include <vector>

namespace bidirectional {

/**
 * Generic callback for custom Resource Extensions.
 * In the case the user has not defined all three, default additive REFs are
 * used.
 */
class REFCallback {
 public:
  REFCallback() {}
  virtual ~REFCallback() {}

  /// Default implementation of a forward REF
  virtual std::vector<double> REF_fwd(
      const std::vector<double>& cumulative_resource,
      const int&                 tail,
      const int&                 head,
      const std::vector<double>& edge_resource_consumption,
      const std::vector<int>&    partial_path,
      const double&              accummulated_cost) const;

  /// Default implementation of a backward REF (note that critical resource
  /// information is not an argument)
  virtual std::vector<double> REF_bwd(
      const std::vector<double>& cumulative_resource,
      const int&                 tail,
      const int&                 head,
      const std::vector<double>& edge_resource_consumption,
      const std::vector<int>&    partial_path,
      const double&              accummulated_cost) const;

  /// Default implementation of a joining REF (used to merge forward and
  /// backward paths)
  virtual std::vector<double> REF_join(
      const std::vector<double>& fwd_resource,
      const std::vector<double>& bwd_resource,
      const int&                 tail,
      const int&                 head,
      const std::vector<double>& edge_resource_consumption) const;
};

/// Default additive REF for forward labels
std::vector<double> additiveForwardREF(
    const std::vector<double>& cumulative_resource,
    const std::vector<double>& edge_resource_consumption);

/// Default additive REF for backward labels
std::vector<double> additiveBackwardREF(
    const std::vector<double>& cumulative_resource,
    const std::vector<double>& edge_resource_consumption,
    const int&                 critical_res = 0);

} // namespace bidirectional

#endif // BIDIRECTIONAL_REF_CALLBACK_H__
