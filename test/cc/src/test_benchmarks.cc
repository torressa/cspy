#include "test_benchmarks.h"

#include <fstream>
#include <iostream> // cout
#include <sstream>

#include "utils.h" // loadMaxMinRes, skipLines, writeToFile, getElapsedTime, getBestCost

namespace bidirectional {

void loadGraph(
    BiDirectional*     bidirectional,
    const int&         num_nodes,
    const int&         num_arcs,
    const int&         num_resources,
    const std::string& path_to_instance,
    const bool&        forward = true) {
  std::ifstream      instance_file(path_to_instance);
  std::istringstream iss;
  std::string        line;

  skipLines(instance_file, line, 3);
  skipLines(instance_file, line, num_nodes);

  for (int i = 0; i < num_arcs; ++i) {
    std::getline(instance_file, line);
    iss.clear();
    iss.str(line);
    int                 tail, head;
    double              weight;
    std::vector<double> res_cost;
    iss >> tail >> head >> weight;

    // if (forward) {
    res_cost.resize(num_resources);
    for (int j = 0; j < num_resources; ++j) {
      iss >> res_cost[j];
    }
    // } else {
    //   // Monotone resource
    //   res_cost.resize(num_resources + 1);
    //   res_cost[0] = 1.0;
    //   for (int j = 1; j < num_resources + 1; ++j) {
    //     iss >> res_cost[j];
    //   }
    // }

    if (tail == 1)
      bidirectional->addEdge("Source", std::to_string(head), weight, res_cost);
    else if (head == 1)
      ;
    else if (head == num_nodes)
      bidirectional->addEdge(std::to_string(tail), "Sink", weight, res_cost);
    else if (tail == num_nodes)
      ;
    else
      bidirectional->addEdge(
          std::to_string(tail), std::to_string(head), weight, res_cost);
  }
}

// Forward only tests

// TEST_P(TestBenchmarks, testForwardElementary) {
//   const std::string path_to_instance =
//       path_to_data + "rcsp" + std::to_string(instance_number) + ".txt";
//   int                 num_nodes, num_arcs, num_resources;
//   std::vector<double> max_res, min_res;
//   loadMaxMinRes(
//       &max_res,
//       &min_res,
//       &num_nodes,
//       &num_arcs,
//       &num_resources,
//       path_to_instance);
//   bidirectional =
//       std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
//   bidirectional->direction  = "forward";
//   bidirectional->elementary = true;
//   bidirectional->time_limit = time_limit;
//   loadGraph(
//       bidirectional.get(),
//       num_nodes,
//       num_arcs,
//       num_resources,
//       path_to_instance);
//   clock_t start = clock();
//   bidirectional->run();
//   auto cost = bidirectional->getTotalCost();
//   ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
//   writeToFile(
//       output_path,
//       "results_fwd_elem.txt",
//       std::to_string(instance_number) + " " +
//           std::to_string(getElapsedTime(start)));
// }
//
// TEST_P(TestBenchmarks, testForward) {
//   const std::string path_to_instance =
//       path_to_data + "rcsp" + std::to_string(instance_number) + ".txt";
//   int                 num_nodes, num_arcs, num_resources;
//   std::vector<double> max_res, min_res;
//   loadMaxMinRes(
//       &max_res,
//       &min_res,
//       &num_nodes,
//       &num_arcs,
//       &num_resources,
//       path_to_instance);
//   bidirectional =
//       std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
//   bidirectional->direction  = "forward";
//   bidirectional->time_limit = time_limit;
//   loadGraph(
//       bidirectional.get(),
//       num_nodes,
//       num_arcs,
//       num_resources,
//       path_to_instance);
//   clock_t start = clock();
//   bidirectional->run();
//   auto cost = bidirectional->getTotalCost();
//   ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
//   writeToFile(
//       output_path,
//       "results_fwd.txt",
//       std::to_string(instance_number) + " " +
//           std::to_string(getElapsedTime(start)));
// }
//
// TEST_P(TestBenchmarks, testForwardBoundsPruning) {
//   const std::string path_to_instance =
//       path_to_data + "rcsp" + std::to_string(instance_number) + ".txt";
//   int                 num_nodes, num_arcs, num_resources;
//   std::vector<double> max_res, min_res;
//   loadMaxMinRes(
//       &max_res,
//       &min_res,
//       &num_nodes,
//       &num_arcs,
//       &num_resources,
//       path_to_instance);
//   bidirectional =
//       std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
//   bidirectional->direction      = "forward";
//   bidirectional->time_limit     = time_limit;
//   bidirectional->bounds_pruning = true;
//   loadGraph(
//       bidirectional.get(),
//       num_nodes,
//       num_arcs,
//       num_resources,
//       path_to_instance);
//
//   clock_t start = clock();
//   bidirectional->run();
//   auto cost = bidirectional->getTotalCost();
//   ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
//   writeToFile(
//       output_path,
//       "results_fwd_bp.txt",
//       std::to_string(instance_number) + " " +
//           std::to_string(getElapsedTime(start)));
// }
//
// /* Both */
//
// TEST_P(TestBenchmarks, testBothElementary) {
//   const std::string path_to_instance =
//       path_to_data + "rcsp" + std::to_string(instance_number) + ".txt";
//   int                 num_nodes, num_arcs, num_resources;
//   std::vector<double> max_res, min_res;
//   loadMaxMinRes(
//       &max_res,
//       &min_res,
//       &num_nodes,
//       &num_arcs,
//       &num_resources,
//       path_to_instance,
//       false);
//   max_res[0] = std::ceil(max_res[0] / 2.0);
//   bidirectional =
//       std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
//   bidirectional->elementary = true;
//   bidirectional->time_limit = time_limit;
//   loadGraph(
//       bidirectional.get(),
//       num_nodes,
//       num_arcs,
//       num_resources,
//       path_to_instance,
//       false);
//   clock_t start = clock();
//   bidirectional->run();
//   auto cost = bidirectional->getTotalCost();
//   auto path = bidirectional->getPath();
//   for (auto p : path) {
//     std::cout << p << ",";
//   }
//   std::cout << "\n";
//   ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
//   writeToFile(
//       output_path,
//       "results_both_elem.txt",
//       std::to_string(instance_number) + " " +
//           std::to_string(getElapsedTime(start)));
// }

TEST_P(TestBenchmarks, testBoth) {
  const std::string path_to_instance =
      path_to_data + "rcsp" + std::to_string(instance_number) + ".txt";
  int                 num_nodes, num_arcs, num_resources;
  std::vector<double> max_res, min_res;
  loadMaxMinRes(
      &max_res,
      &min_res,
      &num_nodes,
      &num_arcs,
      &num_resources,
      path_to_instance,
      false);
  // max_res[0] = std::ceil(max_res[0] / 2.0);
  bidirectional =
      std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
  bidirectional->time_limit = time_limit;
  bidirectional->method     = "processed";
  loadGraph(
      bidirectional.get(),
      num_nodes,
      num_arcs,
      num_resources,
      path_to_instance,
      false);
  clock_t start = clock();
  bidirectional->run();
  auto cost = bidirectional->getTotalCost();
  auto path = bidirectional->getPath();
  for (auto p : path) {
    std::cout << p << ",";
  }
  std::cout << "\n";
  ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  writeToFile(
      output_path,
      "results_both.txt",
      std::to_string(instance_number) + " " +
          std::to_string(getElapsedTime(start)));
}

// TEST_P(TestBenchmarks, testBothBoundsPruning) {
//   const std::string path_to_instance =
//       path_to_data + "rcsp" + std::to_string(instance_number) + ".txt";
//   int                 num_nodes, num_arcs, num_resources;
//   std::vector<double> max_res, min_res;
//   loadMaxMinRes(
//       &max_res,
//       &min_res,
//       &num_nodes,
//       &num_arcs,
//       &num_resources,
//       path_to_instance,
//       false);
//   // max_res[0] = std::ceil(max_res[0] / 2.0);
//   bidirectional =
//       std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
//   bidirectional->elementary     = true;
//   bidirectional->time_limit     = time_limit;
//   bidirectional->bounds_pruning = true;
//   loadGraph(
//       bidirectional.get(),
//       num_nodes,
//       num_arcs,
//       num_resources,
//       path_to_instance,
//       false);
//   clock_t start = clock();
//   bidirectional->run();
//
//   auto cost = bidirectional->getTotalCost();
//   ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
//   writeToFile(
//       output_path,
//       "results_both_bp.txt",
//       std::to_string(instance_number) + " " +
//           std::to_string(getElapsedTime(start)));
// }

INSTANTIATE_TEST_SUITE_P(
    TestBenchmarksBeasley,
    TestBenchmarks,
    ::testing::Range(1, 25));

} // namespace bidirectional
