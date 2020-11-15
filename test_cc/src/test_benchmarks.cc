#include "test_benchmarks.h"

#include <cassert> // assert
#include <fstream>
#include <iostream>
#include <sstream>

namespace bidirectional {

void skipLines(std::ifstream& file, std::string& line, const int& num_lines) {
  for (int i = 0; i < num_lines; ++i) {
    std::getline(file, line);
  }
}

void loadMaxMinRes(
    std::vector<double>* max_res,
    std::vector<double>* min_res,
    int*                 num_nodes,
    int*                 num_arcs,
    int*                 num_resources,
    const std::string&   path_to_instance) {
  std::ifstream      instance_file(path_to_instance);
  std::istringstream iss;
  std::string        line;

  std::getline(instance_file, line);
  iss.str(line);
  iss >> *num_nodes >> *num_arcs >> *num_resources;
  max_res->resize(*num_resources);
  min_res->resize(*num_resources);
  std::getline(instance_file, line);
  iss.clear();
  iss.str(line);
  for (int i = 0; i < *num_resources; ++i) {
    iss >> (*min_res)[i];
  }
  std::getline(instance_file, line);
  iss.clear();
  iss.str(line);
  for (int i = 0; i < *num_resources; ++i) {
    iss >> (*max_res)[i];
  }
  instance_file.close();
}

void loadGraph(
    BiDirectional*     bidirectional,
    const int&         num_nodes,
    const int&         num_arcs,
    const int&         num_resources,
    const std::string& path_to_instance) {
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
    std::vector<double> res_cost(num_resources, 0.0);
    iss >> tail >> head >> weight;
    for (int j = 0; j < num_resources; ++j) {
      iss >> res_cost[j];
    }
    if (tail == 1)
      bidirectional->addEdge("Source", std::to_string(head), weight, res_cost);
    else if (head == 1)
      bidirectional->addEdge(std::to_string(tail), "Source", weight, res_cost);
    else if (head == num_nodes)
      bidirectional->addEdge(std::to_string(tail), "Sink", weight, res_cost);
    else if (tail == num_nodes)
      bidirectional->addEdge("Sink", std::to_string(head), weight, res_cost);
    else
      bidirectional->addEdge(
          std::to_string(tail), std::to_string(head), weight, res_cost);
  }
}

double getBestCost(
    const std::string& path_to_data,
    const int&         instance_number) {
  const std::string& path_to_results = path_to_data + "results.txt";
  std::ifstream      results_file(path_to_results);
  std::istringstream iss;
  std::string        line;
  double             best_cost;
  int                instance_number_;

  skipLines(results_file, line, instance_number);
  std::getline(results_file, line);
  iss.str(line);
  iss >> instance_number_ >> best_cost;
  assert(instance_number_ == instance_number);
  return best_cost;
}

TEST_P(TestBenchmarks, testForwardElementary) {
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
      path_to_instance);
  bidirectional =
      std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
  bidirectional->direction  = "forward";
  bidirectional->elementary = true;
  bidirectional->time_limit = time_limit;
  loadGraph(
      bidirectional.get(),
      num_nodes,
      num_arcs,
      num_resources,
      path_to_instance);
  bidirectional->run();
  auto cost = bidirectional->getTotalCost();
  ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
}

TEST_P(TestBenchmarks, testForward) {
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
      path_to_instance);
  bidirectional =
      std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
  bidirectional->direction  = "forward";
  bidirectional->time_limit = time_limit;
  loadGraph(
      bidirectional.get(),
      num_nodes,
      num_arcs,
      num_resources,
      path_to_instance);
  std::cout << "loaded graph\n";
  bidirectional->run();
  auto cost = bidirectional->getTotalCost();
  ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
}

TEST_P(TestBenchmarks, testBothElementaryUnprocessed) {
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
      path_to_instance);
  bidirectional =
      std::make_unique<BiDirectional>(num_nodes, num_arcs, max_res, min_res);
  bidirectional->elementary = true;
  bidirectional->method     = "unprocessed";
  bidirectional->time_limit = time_limit;
  loadGraph(
      bidirectional.get(),
      num_nodes,
      num_arcs,
      num_resources,
      path_to_instance);
  bidirectional->run();
  auto cost = bidirectional->getTotalCost();
  ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
}

// TEST_P(TestBenchmarks, testBoth) {
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
//   bidirectional->method = "unprocessed";
//   loadGraph(
//       bidirectional.get(),
//       num_nodes,
//       num_arcs,
//       num_resources,
//       path_to_instance);
//   bidirectional->run();
//   auto cost = bidirectional->getTotalCost();
//   ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
// }

INSTANTIATE_TEST_SUITE_P(
    TestBenchmarksName,
    TestBenchmarks,
    ::testing::Range(1, 10));

} // namespace bidirectional
