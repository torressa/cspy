#ifndef BIDIRECTIONAL_BIDIRECTIONAL_H__
#define BIDIRECTIONAL_BIDIRECTIONAL_H__

#include <cmath> // nan
#include <ctime> // clock_t
#include <vector>

#include "digraph.h"
#include "labelling.h"
#include "ref_callback.h"
#include "search.h"

namespace bidirectional {

class BiDirectional {
 public:
  /**
   * BiDirectional algorithm. see docs
   * For use called in a the following order:
   * 1. ctor (memory allocation for the graph)
   * 2. [optional] set solving parameters if desired (e.g. time_limit, ...)
   * 	2.1. [optional] set callback using `setREFCallback`
   * 	2.2. [optional] set seed using `setSeed`
   * 3. add edges at will using `addEdge`.
   * 4. call `run`
   *
   * @param[in] number_vertices, int number of vertices in the graph (to be
   * added using addEdge)
   * @param[in] number_edges, int number of edges in the graph
   * @param[in] max_res, vector of double with upper bound for resource
   * consumption
   * @param[in] min_res, vector of double with lower bound for resource
   * consumption
   */
  BiDirectional(
      const int&                 number_vertices,
      const int&                 number_edges,
      const std::vector<double>& max_res,
      const std::vector<double>& min_res);
  ~BiDirectional();

  /// DiGraph pointer (raw cause of swig!)
  DiGraph* graph;

  // Inputs
  /// vector with upper and lower bounds for resources
  std::vector<double> max_res;
  std::vector<double> min_res;
  /// string with direction of search
  // Optional inputs (set manually)
  std::string direction = "both";
  /// string with method to determine the next direction of search
  std::string method = "unprocessed";
  /// double with time limit in seconds
  double time_limit = std::nan("na");
  /// double with threshold to stop search with total cost <= threshold
  double threshold = std::nan("na");
  /// bool with whether output path is required to be elementary
  bool elementary = false;
  /// int multiples of the iterations where dominance function is run
  int dominance_frequency = 1;

  /// set seed
  void setSeed(const int& seed = 1);
  /// Pass python callback for label extensions.
  /// Note: swig needs namespace specifier
  void setREFCallback(bidirectional::REFCallback* cb) const;
  /// Add an edge to the graph
  void addEdge(
      const std::string&         tail,
      const std::string&         head,
      const double&              weight,
      const std::vector<double>& resource_consumption);
  /// Initalise searches
  void initSearches();
  /// run the algorithm (assumes all the appropriate options are set)
  void run();
  /// Return the final path
  std::vector<std::string> getPath() const;
  /// Return the consumed resources
  std::vector<double> getConsumedResources() const;
  /// Return the total cost
  double getTotalCost() const;

 private:
  /// Intermediate current best label with possibly complete source-sink path
  /// (shared pointer as we want to be able to substitute it without reseting)
  std::shared_ptr<labelling::Label> intermediate_label_;
  /// Final best label (merged or otherwise)
  std::shared_ptr<labelling::Label> best_label_;
  /// @see labelling::LabelExtension
  std::unique_ptr<labelling::LabelExtension> label_extension_;
  // Algorithm parameters
  // whether the search terminad early with a valid s-t path
  bool                                 terminated_early_w_st_path_ = false;
  clock_t                              start_time_;
  std::unique_ptr<Search>              fwd_search_;
  std::unique_ptr<Search>              bwd_search_;
  std::unique_ptr<std::vector<double>> lower_bound_weight_;

  // Algorithm methods
  /// Get the next direction to search
  std::string getDirection() const;
  /// Advance the search in a given direction
  void move(const std::string& direction_);
  // void checkTerminateSerial();
  void updateIntermediateLabel();
  /// checks if the time_limit if over (if set) or if a label under the
  /// threshold has been found (if set). Sets terminated_early_w_st_path_
  bool terminate(const labelling::Label& label);
  bool checkValidLabel(const labelling::Label& label);
  /// @see Search.cleanUp
  void cleanUp() const;
  /**
   * Wrapper to process of output path. Either saves appropriate label
   * (single-direction search or early termination) or calls joinLabels to merge
   * forward + backward labels
   */
  void postProcessing();
  /// get upper bound for a source-sink path (looks at both forward and backward
  /// source-sink paths)
  double getUB();
  /**
   * get minimum weight across all forward / backward labels
   * @param[out] fwd_min, double, minimum accross all forward labels
   * @param[out] bwd_min, double, minimum accross all backward labels
   */
  void getMinimumWeights(double* fwd_min, double* bwd_min);
  /**
   * The procedure "Join" or Algorithm 3 from `Righini and Salani (2006)`_.
   *
   * @return: list with the final path.
   * @see: https://www.sciencedirect.com/science/article/pii/S1572528606000417
   */
  void joinLabels();
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_BIDIRECTIONAL_H__
