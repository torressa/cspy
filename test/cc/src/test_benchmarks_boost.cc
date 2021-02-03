#include "test_benchmarks_boost.h"

#include <boost/config.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/r_c_shortest_paths.hpp>
#include <fstream>
#include <iostream> // cout
#include <sstream>
#include <vector>

#include "utils.h" // loadMaxMinRes, skipLines, writeToFile, getElapsedTime, getBestCost

namespace boost {

// Define all the necessary data structures
// Based on:
struct MyVertex {
  MyVertex(const int& n = 0) : id(n) {}
  int id;
};

struct MyAdjVertex {
  MyAdjVertex(
      const int&                 n = 0,
      const double&              w = 0.0,
      const std::vector<double>& r = {})
      : id(n), weight(w), res(r) {}
  int                 id;
  double              weight;
  std::vector<double> res;
};

typedef adjacency_list<vecS, vecS, directedS, MyVertex, MyAdjVertex> MyGraph;

// ResourceContainer model
struct MyResourceContainer {
  MyResourceContainer(
      const double&              w          = 0.0,
      const std::vector<double>& r          = {},
      const std::vector<double>& min_res_in = {},
      const std::vector<double>& max_res_in = {})
      : weight(w), res(r), min_res(min_res_in), max_res(max_res_in) {}

  MyResourceContainer& operator=(const MyResourceContainer& other) {
    if (this == &other)
      return *this;
    this->~MyResourceContainer();
    new (this) MyResourceContainer(other);
    return *this;
  }

  double weight;
  // Current resource usage
  std::vector<double> res;
  // Bounds
  std::vector<double> min_res;
  std::vector<double> max_res;
};

bool operator==(
    const MyResourceContainer& res_cont_1,
    const MyResourceContainer& res_cont_2) {
  if (res_cont_1.weight != res_cont_2.weight) {
    return false;
  }
  // Check resources one by one
  const int& num_res = res_cont_1.res.size();
  for (int r = 0; r < num_res; ++r) {
    if (res_cont_1.res[r] != res_cont_2.res[r]) {
      return false;
    }
  }
  return true;
}

bool operator<(
    const MyResourceContainer& res_cont_1,
    const MyResourceContainer& res_cont_2) {
  if (res_cont_1.weight > res_cont_2.weight) {
    return false;
  }
  const int& num_res = res_cont_1.res.size();
  for (int r = 0; r < num_res; ++r) {
    if (res_cont_1.res[r] >= res_cont_2.res[r]) {
      return false;
    }
  }
  return true;
}

// ResourceExtensionFunction model
class MyResourceExtensionFunction {
 public:
  inline bool operator()(
      const MyGraph&                         g,
      MyResourceContainer&                   new_cont,
      const MyResourceContainer&             old_cont,
      graph_traits<MyGraph>::edge_descriptor ed) const {
    const MyAdjVertex& arc_prop  = get(edge_bundle, g)[ed];
    const MyVertex&    vert_prop = get(vertex_bundle, g)[target(ed, g)];
    new_cont.weight              = old_cont.weight + arc_prop.weight;
    // Pass min / max resources
    new_cont.min_res = old_cont.min_res;
    new_cont.max_res = old_cont.max_res;

    std::vector<double> new_resources = old_cont.res;
    std::transform(
        new_resources.begin(),
        new_resources.end(),
        arc_prop.res.begin(),
        new_resources.begin(),
        std::plus<double>());
    new_cont.res = new_resources;
    // Check resource feasibility
    const int&                 num_res = old_cont.res.size();
    const std::vector<double>& min_res = old_cont.min_res;
    const std::vector<double>& max_res = old_cont.max_res;
    for (int r = 0; r < num_res; ++r) {
      if (min_res[r] <= new_cont.res[r] && new_cont.res[r] <= max_res[r]) {
        ;
      } else {
        return false;
      }
    }
    return true;
  }
};

// DominanceFunction model
class MyDominanceFunction {
 public:
  inline bool operator()(
      const MyResourceContainer& res_cont_1,
      const MyResourceContainer& res_cont_2) const {
    const int& num_res = res_cont_1.res.size();
    if (res_cont_1.weight > res_cont_2.weight) {
      return false;
    }
    for (int i = 0; i < num_res; i++) {
      if (res_cont_1.res[i] > res_cont_2.res[i]) {
        return false;
      }
    }
    return true;
  }
};

void loadGraph(
    MyGraph&           my_graph,
    const int&         num_nodes,
    const int&         num_arcs,
    const int&         num_resources,
    const std::string& path_to_instance) {
  // Init nodes
  for (int i = 1; i <= num_nodes; ++i) {
    boost::add_vertex(boost::MyVertex(i), my_graph);
  }
  // Load graph
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
    if (tail == 1) {
      add_edge(1, head, MyAdjVertex(i, weight, res_cost), my_graph);
    } else if (head == 1) {
      ;
    } else if (head == num_nodes) {
      add_edge(tail, num_nodes, MyAdjVertex(i, weight, res_cost), my_graph);
    } else if (tail == num_nodes) {
      ;
    } else {
      add_edge(tail, head, MyAdjVertex(i, weight, res_cost), my_graph);
    }
  }
}

TEST_P(TestBenchmarksBoost, test_r_c_shortest_paths) {
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

  MyGraph my_graph;
  loadGraph(my_graph, num_nodes, num_arcs, num_resources, path_to_instance);

  clock_t start = clock();
  std::vector<std::vector<graph_traits<MyGraph>::edge_descriptor>>
                                   opt_solutions;
  std::vector<MyResourceContainer> pareto_opt;
  // Source, sink
  graph_traits<MyGraph>::vertex_descriptor s = 1;
  graph_traits<MyGraph>::vertex_descriptor t = num_nodes;

  std::vector<double> zeros(num_resources, 0.0);

  r_c_shortest_paths(
      my_graph,
      get(&MyVertex::id, my_graph),
      get(&MyAdjVertex::id, my_graph),
      s,
      t,
      opt_solutions,
      pareto_opt,
      MyResourceContainer(0.0, zeros, min_res, max_res),
      MyResourceExtensionFunction(),
      MyDominanceFunction(),
      std::allocator<r_c_shortest_paths_label<MyGraph, MyResourceContainer>>(),
      default_r_c_shortest_paths_visitor());

  double     cost               = 1000000.0;
  const int& opt_solutions_size = opt_solutions.size();
  for (int i = 0; i < opt_solutions_size; ++i) {
    if (pareto_opt[i].weight < cost) {
      cost = pareto_opt[i].weight;
    }
  }
  if (instance_number == 14) {
    ASSERT_EQ(opt_solutions_size, 0);
  } else {
    ASSERT_EQ(cost, getBestCost(path_to_data, instance_number));
  }
  writeToFile(
      "/root/build/",
      "results_boost.txt",
      std::to_string(instance_number) + " " +
          std::to_string(getElapsedTime(start)));
}

INSTANTIATE_TEST_SUITE_P(
    TestBenchmarksBeasleyBoost,
    TestBenchmarksBoost,
    ::testing::Range(1, 25));

} // namespace boost
