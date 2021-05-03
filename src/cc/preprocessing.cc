#include "preprocessing.h"

#include <iostream>
#include <queue>
#include <set>

#include "digraph.h"
#include "lemon/adaptors.h"     // reverseDigraph
#include "lemon/bellman_ford.h" // BellmanFord

namespace bidirectional {

void shortest_path(
    std::vector<double>* lower_bound_weight,
    const DiGraph&       graph,
    const bool&          forward) {
  // Create map to store distances
  LemonGraph::NodeMap<double> distance_map(*graph.lemon_graph_ptr);
  // ref source + sink
  const LemonNode& source = graph.getLNodeFromId(graph.source.lemon_id);
  const LemonNode& sink   = graph.getLNodeFromId(graph.sink.lemon_id);
  if (forward) {
    // Instantiate algorithm with normal graph
    bellmanFord(*graph.lemon_graph_ptr, *graph.weight_map_ptr)
        .distMap(distance_map)
        .run(source, sink);
  } else {
    // Instantiate algorithm with reversed digraph
    bellmanFord(reverseDigraph(*graph.lemon_graph_ptr), *graph.weight_map_ptr)
        .distMap(distance_map)
        .run(sink, source);
  }
  // Extract shortest path distance to each node, if available, ow lemon::inf
  for (LemonGraph::NodeIt v(*graph.lemon_graph_ptr); v != lemon::INVALID; ++v) {
    const int& id = graph.getId(v);
    // std::cout << "dist[" << id << "] = " << distance_map[v] << "\n";
    (*lower_bound_weight)[id] = distance_map[v];
  }
}

} // namespace bidirectional
