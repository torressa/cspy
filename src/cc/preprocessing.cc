#include "preprocessing.h"

#include <iostream>
#include <queue>
#include <set>

#include "digraph.h"
#include "lemon/adaptors.h"     // reverseDigraph
#include "lemon/bellman_ford.h" // BellmanFord

namespace bidirectional {

// TODO Use explicit types when calling BF to avoid error on MACOS

void shortest_path(
    std::vector<double>* lower_bound_weight,
    const DiGraph&       graph,
    const bool&          forward) {
  // Create map to store distances
  if (forward) {
    // Instantiate algorithm with normal graph
    LemonGraph::NodeMap<double> distance_map(*graph.lemon_graph_ptr);
    const LemonNode& source = graph.getLNodeFromId(graph.source.lemon_id);
    lemon::BellmanFord<LemonGraph, LemonGraph::ArcMap<double>> BF(
        *graph.lemon_graph_ptr, *graph.weight_map_ptr);
    BF.distMap(distance_map);
    BF.run(source, graph.number_edges);
    // TODO: Fix wizard version on MACOS
    // bellmanFord(*graph.lemon_graph_ptr, *graph.weight_map_ptr)
    //     .distMap(distance_map)
    //     .run(source, sink);

    // Extract shortest path distance to each node, if available, ow lemon::inf
    for (LemonGraph::NodeIt v(*graph.lemon_graph_ptr); v != lemon::INVALID;
         ++v) {
      const int& id = graph.getId(v);
      // std::cout << "dist[" << id << "] = " << distance_map[v] << "\n";
      (*lower_bound_weight)[id] = distance_map[v];
    }
  } else {
    lemon::ReverseDigraph<const LemonGraph> RG(*graph.lemon_graph_ptr);
    lemon::ReverseDigraph<const LemonGraph>::NodeMap<double> distance_map_rev(
        *graph.lemon_graph_ptr);
    const LemonNode& sink = graph.getLNodeFromId(graph.sink.lemon_id);

    lemon::BellmanFord<
        lemon::ReverseDigraph<const LemonGraph>,
        LemonGraph::ArcMap<double>>
        BF(RG, *graph.weight_map_ptr);
    BF.distMap(distance_map_rev);
    BF.run(sink, graph.number_edges);

    // TODO: Fix wizard version on MACOS
    // Instantiate algorithm with reversed digraph
    // bellmanFord(reverseDigraph(*graph.lemon_graph_ptr),
    // *graph.weight_map_ptr)
    //     .distMap(distance_map)
    //     .run(sink, source);

    // Extract distance using reverse map
    for (LemonGraph::NodeIt v(*graph.lemon_graph_ptr); v != lemon::INVALID;
         ++v) {
      const int& id = graph.getId(v);
      // std::cout << "dist[" << id << "] = " << distance_map_rev[v] << "\n";
      (*lower_bound_weight)[id] = distance_map_rev[v];
    }
  }
}

} // namespace bidirectional
