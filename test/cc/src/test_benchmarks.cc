#include <fstream>
#include <sstream>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"
#include "utils.h" // loadMaxMinRes, skipLines, writeToFile, getElapsedTime, getBestCost

namespace bidirectional {

/**
 * TestBenchmarks fixture class for unittests. Inherits from gtest.
 */
class TestBenchmarks : public ::testing::TestWithParam<int> {
 public:
  int               instance_number;
  const int         number_repetitions = 100;
  const std::string path_to_data =
      "/root/benchmarks/beasley_christofides_1989/";
  const std::string output_path = "/root/build/";
  // const std::string path_to_data =
  //     "/home/torressa/Documents/code/cspy/benchmarks/"
  //     "beasley_christofides_1989/";
  // const std::string output_path =
  // "/home/torressa/Documents/code/cspy/build/";
  std::unique_ptr<BiDirectional> bidirectional;

  void SetUp() override { instance_number = GetParam(); }
};

/// Set critical resources by hand
void setCriticalRes(BiDirectional* bidirectional, int instance_number) {
  if (instance_number == 5 || instance_number == 6)
    bidirectional->setCriticalRes(7);
  if (instance_number == 7)
    bidirectional->setCriticalRes(1);
  if (instance_number == 8)
    bidirectional->setCriticalRes(2);
  if (instance_number == 13)
    bidirectional->setCriticalRes(3);
  if (instance_number == 14)
    bidirectional->setCriticalRes(0);
  if (instance_number == 15 || instance_number == 16)
    bidirectional->setCriticalRes(2);
  if (instance_number == 23 || instance_number == 24)
    bidirectional->setCriticalRes(7);
}

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

  std::vector<int> nodes;
  for (int n = 1; n <= num_nodes; ++n) {
    nodes.push_back(n);
  }
  bidirectional->addNodes(nodes);

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
      bidirectional->addEdge(1, head, weight, res_cost);
    else if (head == 1)
      ;
    else if (head == num_nodes)
      bidirectional->addEdge(tail, num_nodes, weight, res_cost);
    else if (tail == num_nodes)
      ;
    else
      bidirectional->addEdge(tail, head, weight, res_cost);
  }
}

// Forward only tests

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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    bidirectional->setDirection("forward");
    bidirectional->setElementary(true);
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance);
    clock_t start = clock();
    bidirectional->run();
    const double elapsed_time = getElapsedTime(start);
    average_time += (elapsed_time - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_fwd_elem.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    bidirectional->setDirection("forward");
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance);
    clock_t start = clock();
    bidirectional->run();
    average_time += (getElapsedTime(start) - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_fwd.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
}

TEST_P(TestBenchmarks, testForwardBoundsPruning) {
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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    bidirectional->setDirection("forward");
    bidirectional->setBoundsPruning(true);
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance);

    clock_t start = clock();
    bidirectional->run();
    average_time += (getElapsedTime(start) - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_fwd_bp.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
}

/* Both */

TEST_P(TestBenchmarks, testBothElementary) {
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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    bidirectional->setElementary(true);
    // bidirectional->setFindCriticalRes(true);
    // setCriticalRes(bidirectional.get(), instance_number);
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance,
        false);
    clock_t start = clock();
    bidirectional->run();
    average_time += (getElapsedTime(start) - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_both_elem.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
}

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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance,
        false);
    clock_t start = clock();
    bidirectional->run();
    average_time += (getElapsedTime(start) - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_both.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
}

TEST_P(TestBenchmarks, testBothFindCriticalRes) {
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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    bidirectional->setFindCriticalRes(true);
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance,
        false);
    clock_t start = clock();
    bidirectional->run();
    average_time += (getElapsedTime(start) - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_both_critical.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
}

TEST_P(TestBenchmarks, testBothBoundsPruning) {
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
  double average_time = 0.0;
  for (int i = 1; i < number_repetitions + 1; ++i) {
    bidirectional = std::make_unique<BiDirectional>(
        num_nodes, num_arcs, 1, num_nodes, max_res, min_res);
    bidirectional->setElementary(true);
    bidirectional->setBoundsPruning(true);
    // setCriticalRes(bidirectional.get(), instance_number);
    bidirectional->setFindCriticalRes(true);
    loadGraph(
        bidirectional.get(),
        num_nodes,
        num_arcs,
        num_resources,
        path_to_instance,
        false);
    clock_t start = clock();
    bidirectional->run();
    average_time += (getElapsedTime(start) - average_time) / i;
    auto cost = bidirectional->getTotalCost();
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      output_path,
      "results_both_bp.txt",
      std::to_string(instance_number) + " " + std::to_string(average_time));
}

INSTANTIATE_TEST_SUITE_P(
    TestBenchmarksBeasley,
    TestBenchmarks,
    ::testing::Range(1, 25));

} // namespace bidirectional
