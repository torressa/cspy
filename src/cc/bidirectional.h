#ifndef BIDIRECTIONAL_BIDIRECTIONAL_H__
#define BIDIRECTIONAL_BIDIRECTIONAL_H__

#include <chrono> // timing (e.g. time_point)
#include <cmath>  // nan
#include <set>
#include <vector>

#include "digraph.h"
#include "labelling.h"
#include "ref_callback.h"
#include "search.h"

namespace bidirectional {

/// Parameters for tuning the search
struct SolvingOptions {
  /// string with direction of search. Either: forward, backward, or both
  std::string direction = "both";
  /// string with method to determine the next direction of search
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
};

/**
 * BiDirectional algorithm. see docs
 *
 * 1. ctor (memory allocation for the graph)
 * 2. add edges to graph using `addEdge`.
 * 3. [optional] set solving parameters if desired (e.g. time_limit, ...)
 * 	3.1. [optional] set callback using `setREFCallback`
 * 	3.2. [optional] set seed using `setSeed`
 * 4. call `run`
 */
class BiDirectional {
 public:
  /**
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
      const int&                 source_id,
      const int&                 sink_id,
      const std::vector<double>& max_res_in,
      const std::vector<double>& min_res_in);

  /// Default destructor
  ~BiDirectional(){};

  /* Parameters */
  /// vector with upper and lower bounds for resources
  std::vector<double> max_res;
  std::vector<double> min_res;
  int                 source_id;
  int                 sink_id;
  /// Search options for the algorithm
  SolvingOptions options;

  /* Methods */

  /// set random using a given seed
  void setSeed(const int& seed) { std::srand(seed); }
  /// Pass python callback for label extensions.
  /// Note: swig needs namespace specifier
  void setREFCallback(bidirectional::REFCallback* cb) const;
  /// Wrapper to add nodes to the graph. @see DiGraph::addNodes
  void addNodes(const std::vector<int>& nodes) { graph_ptr_->addNodes(nodes); }
  /// Add an edge to the graph
  void addEdge(
      const int&                 tail,
      const int&                 head,
      const double&              weight,
      const std::vector<double>& resource_consumption) {
    graph_ptr_->addEdge(tail, head, weight, resource_consumption);
  }
  /// run the algorithm (assumes all the appropriate options are set)
  void run();

  /* Getters */

  /// Return the final path
  std::vector<int> getPath() const;
  /// Return the consumed resources
  std::vector<double> getConsumedResources() const;
  /// Return the total cost
  double getTotalCost() const;

 private:
  /// Pointer to graph
  std::unique_ptr<DiGraph> graph_ptr_;
  /// Start time to ensure time limit is met
  std::chrono::time_point<std::chrono::system_clock> start_time_;
  /**
   * All the following parameters a size two vectors (easier access as opposed
   * to a pair for example) containing the appropriate parameters for the
   * bidirectional search.
   *
   * - index 0: contains forward attributes
   * - index 1: contains backward attributes
   *
   * In the case of single direction, the vectors have size 1 and the index
   * correspond to the chosen direction.
   */
  std::vector<std::string> directions_;
  int                      directions_size_ = 1;
  /// stopping criteria for each direction
  std::vector<bool> stop_;
  /// stopping criteria for each direction
  std::vector<bool> bound_exceeded_;
  /// Number of unprocessed labels generated
  std::vector<int> unprocessed_count_;
  /// Number of labels processed
  std::vector<int> processed_count_;
  /// Number of labels generated (includes the possibly infeasible extensions)
  std::vector<int> generated_count_;
  /// Current primal bound for a complete source-sink path
  double primal_bound_ = std::nan("nan");
  /// iteration number
  int iteration_ = 0;
  /// whether intermediate_label_fwd/bwd contains a source-sink feasible path
  bool primal_st_bound_ = false;
  // whether the search terminated early with a valid source-sink path
  bool terminated_early_w_st_path_               = false;
  int  terminated_early_w_st_path_direction_idx_ = 0;

  /* Search-related parameters */

  /// Lower bounds from any node to sink
  std::vector<std::unique_ptr<std::vector<double>>> lower_bound_weight_;
  /// vector with indices of vertices visited
  std::vector<std::set<int>> visited_vertices_;
  // current resources
  std::vector<double> max_res_curr_, min_res_curr_;

  /* labels and containers */

  /// Final best label (merged or otherwise)
  std::shared_ptr<labelling::Label> best_label_;
  /// @see labelling::LabelExtension
  std::unique_ptr<labelling::LabelExtension> label_extension_;

  /// Label that is being extended
  std::vector<std::shared_ptr<labelling::Label>> current_label_;
  /// Intermediate current best label with possibly complete source-sink path
  /// (shared pointer as we want to be able to substitute it without resetting)
  std::vector<std::shared_ptr<labelling::Label>> intermediate_label_;

  /// vector with pareto optimal labels (per node)
  std::vector<std::vector<std::vector<labelling::Label>>> efficient_labels_;
  /// vector with pointer to label with least weight (per node)
  std::vector<std::vector<std::shared_ptr<labelling::Label>>> best_labels_;
  /**
   * heap vector to keep unprocessed labels ordered.
   * the order depends on the on the direction of the search.
   * i.e. forward -> increasing in the monotone resource,
   * backward -> decreasing in the monotone resource.
   */
  std::vector<std::unique_ptr<std::vector<labelling::Label>>>
      unprocessed_labels_;

  /* Initialisation Methods */

  /// Wrapper to initialise search in the appropriate direction
  void initSearches();
  /// Initialise labels with appropriate resources
  void initResourceBounds();
  /// Make `unprocessed_labels_` a heap
  void initContainers();
  /// Construct first label and initialise `unprocessed_labels_` heap,
  /// `best_labels` source bucket and `visited_vertices`.
  void initLabels(const int& direction_idx);
  /**
   * Run preprocessing steps if required. Currently includes:
   *   - Obtain shortest paths bounds
   * TODO:
   *   - Bounding and adjusting of resource bounds
   */
  void runPreprocessing();

  /* Search Methods */
  /// Get the next direction to search
  std::string getDirection() const;
  /// Advance the search in a given direction
  void move(const int& direction_idx);
  /// checks if the time_limit if over (if set) or if a label under the
  /// threshold has been found (if set). Sets terminated_early_w_st_path_
  bool terminate(const int& direction_idx, const labelling::Label& label);
  bool checkValidLabel(const int& direction_idx, const labelling::Label& label);
  /// Returns true if half-way points are being violated. False otherwise
  bool checkBounds(const int& direction_idx);
  /// Call labelling::getNextLabel to get next label in the heap
  /// (unprocessed_labels_) and update the current_label member
  void updateCurrentLabel(const int& direction_idx);
  /// Update half-way points and check if the current labels violates them, in
  /// which case sets the stop member to true.
  void updateHalfWayPoints(const int& direction_idx);
  /**
   * Given a candidate_label by looking at the vector of labels (bucket) for
   * that node, we can check if the candidate_label has already been saved or it
   * is dominated.
   * If both of these conditions are false, not seen and not
   * dominated, then we add it to the bucket.
   * Additionally, if the bounds_pruning option is active, we check the bounds
   * here, as an extra condition to add a label to the bucket.
   * Also, `visited_vertices` is updated here.
   */
  void updateEfficientLabels(
      const int&              direction_idx,
      const labelling::Label& candidate_label);
  /// Update `best_labels` entry by node with the current label if appropriate
  void updateBestLabels(
      const int&              direction_idx,
      const labelling::Label& candidate_label);
  /// Iterate over the neighbours for the current label node and save label
  /// extensions when appropriate. This is checked in updateEfficientLabels.
  void extendCurrentLabel(const int& direction_idx);
  /// Helper function to extend along a given arc
  void extendSingleLabel(
      labelling::Label* label,
      const int&        direction_idx,
      const AdjVertex&  adj_vertex);
  /// Save globally best label and check if it is Source-Sink so we can use it
  /// in the bounding. Sets `final_label`
  void saveCurrentBestLabel(const int& direction_idx);
  /**
   * If bounds_pruning is true then check whether an input label plus a lower
   * bound for the path (from the node of the label to the source/sink) violates
   * the current primal bound.
   *
   * @return true if primal bound is violated, false otherwise.
   * i.e. if true, then input label cannot appear in the optimal solution.
   */
  bool checkPrimalBound(
      const int&              direction_idx,
      const labelling::Label& candidate_label) const;

  /* Post processing */

  /**
   * Wrapper to process of output path. Either saves appropriate label
   * (single-direction search or early termination) or calls joinLabels to merge
   * forward + backward labels
   */
  void postProcessing();
  /// get upper bound using a valid source-sink path (looks at both forward and
  /// backward source-sink paths)
  double getUB();
  /**
   * get minimum weight across all forward / backward labels
   * @param[out] fwd_min, double, minimum across all forward labels
   * @param[out] bwd_min, double, minimum across all backward labels
   */
  void getMinimumWeights(double* fwd_min, double* bwd_min);
  /**
   * The procedure "Join" or Algorithm 3 from Righini and Salani (2006).
   *
   * @return: list with the final path.
   * @see: https://www.sciencedirect.com/science/article/pii/S1572528606000417
   */
  void joinLabels();
  /// Sorts efficient_labels for each vertex (not used as it takes too long)
  void cleanUp();
  /// checks if a given vertex has been visited
  /// @return true if it has been visited false otherwise
  bool checkVertexVisited(const int& direction_idx, const int& vertex_idx)
      const;
  /// returns halfway point
  double getHalfWayPoint() const;
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_BIDIRECTIONAL_H__
