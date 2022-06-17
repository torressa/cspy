#ifndef SRC_CC_PARAMS_H__
#define SRC_CC_PARAMS_H__

#include <cmath> // nan
#include <vector>

#include "ref_callback.h"

namespace bidirectional {

/// Internal enum for directions
enum Directions {
  /// Forward
  FWD,
  /// Backward
  BWD,
  /// Both
  BOTH,
  /// No direction
  NODIR
};

/**
 * Input parameters.
 */
class Params {
 public:
  /// Direction for search
  Directions direction = bidirectional::BOTH;
  /// string with method to determine the next direction of search. Options
  /// are: unprocessed, processed and generated.
  std::string method = "unprocessed";
  /// double with time limit in seconds
  double time_limit = std::nan("na");
  /// double with threshold to stop search with total cost <= threshold
  double threshold = std::nan("na");
  /// bool with whether output path is required to be elementary
  bool elementary = false;
  /// bool with whether lower bounds based on shortest paths are used to prune
  /// labels. Experimental!
  bool bounds_pruning = false;
  /// bool with whether critical resource is found at the preprocessing stage.
  /// @see getCriticalRes. overrides critical_res value. Default false.
  bool find_critical_res = false;
  /// Resource id for the critical resource used in dominance checks and
  /// choosing the halfway point. Default is 0.
  int critical_res = 0;
  /// Callback to custom REF
  bidirectional::REFCallback* ref_callback = nullptr;

  /* Constructors */

  Params(){};
  ~Params() {
    ref_callback = nullptr;
    delete ref_callback;
  };

  /* Public methods */

  /* Setters */
  void setDirection(const std::string& direction_in) {
    if (direction_in == "forward")
      direction = FWD;
    else if (direction_in == "backward")
      direction = BWD;
  }
  void setMethod(const std::string& method_in) { method = method_in; }
  void setTimeLimit(const double& time_limit_in) { time_limit = time_limit_in; }
  void setThreshold(const double& threshold_in) { threshold = threshold_in; }
  void setElementary(const bool& elementary_in) { elementary = elementary_in; }
  void setBoundsPruning(const bool& bounds_pruning_in) {
    bounds_pruning = bounds_pruning_in;
  }
  void setFindCriticalRes(const bool& find_critical_res_in) {
    find_critical_res = find_critical_res_in;
  }
  void setCriticalRes(const int& critical_res_in) {
    critical_res = critical_res_in;
  }
  /// Set callback for custom resource extensions
  void setREFCallback(bidirectional::REFCallback* cb) { ref_callback = cb; };
};

} // namespace bidirectional

#endif // SRC_CC_PARAMS_H__
