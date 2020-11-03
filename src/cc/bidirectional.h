#ifndef BIDIRECTIONAL_BIDIRECTIONAL_H__
#define BIDIRECTIONAL_BIDIRECTIONAL_H__

#include <cmath>
#include <ctime>
#include <vector>

#include "digraph.h"
#include "labelling.h"
#include "py_ref_callback.h"
#include "search.h"

namespace bidirectional {

class BiDirectional {
 public:
  BiDirectional(
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
  std::string method = "random";
  /// double with time limit in seconds
  double time_limit = std::nan("na");
  /// double with threshold to stop search with total cost <= threshold
  double threshold = std::nan("na");
  /// bool with whether output path is required to be elementary
  bool elementary = false;
  /// int multiples of the iterations where dominance function is run
  int dominance_frequency = 1;
  // For output
  /// Final label
  std::shared_ptr<labelling::Label> final_label;
  std::shared_ptr<labelling::Label> best_label;

  /// set seed
  void setSeed(const int& seed = 1);
  /// Pass python callback for label extensions.
  /// Note: swig needs namespace specifier
  void setPyCallback(bidirectional::PyREFCallback* cb) const;
  void call() const;
  /// Add an edge to the graph
  void addEdge(
      const std::string&         tail,
      const std::string&         head,
      const double&              weight,
      const std::vector<double>& resource_consumption);
  /// run the algorithm (assumes all the appropriate options are set)
  void run();
  /// Return the final path
  std::vector<std::string> getPath() const;
  /// Return the consumed resources
  std::vector<double> getConsumedResources() const;
  /// Return the total cost
  double getTotalCost() const;

 private:
  /// @see labelling::LabelExtension
  std::shared_ptr<labelling::LabelExtension> label_extension_;
  // Algorithm parameters
  clock_t                 start_time;
  std::unique_ptr<Search> fwd_search_;
  std::unique_ptr<Search> bwd_search_;

  // Algorithm methods
  void initSearches();
  /// Get the next direction to search
  std::string getDirection() const;
  /// Advance the search in a given direction
  void move(const std::string& direction_);
  // void checkTerminateSerial();
  void updateFinalLabel();
  bool terminate() const;
  bool checkFinalLabel() const;
  void cleanUp() const;
  /// Processing of output path.
  void postProcessing();
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
