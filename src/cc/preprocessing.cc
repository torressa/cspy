#include "preprocessing.h"

#include <iostream>
#include <queue>
#include <set>

#include "digraph.h"

namespace bidirectional {

void dijkstra(
    std::vector<double>* lower_bound_weight,
    const DiGraph&       graph,
    const double&        reverse) {
  const int&    number_vertices = graph.number_vertices;
  std::set<int> visited;
  // vertices have idx and distance
  std::vector<Vertex> vertices = graph.vertices;
  for (int i = 0; i < number_vertices; ++i) {
    vertices[i].distance = INF;
  }
  int source_idx;
  if (reverse) {
    // init heap with source
    source_idx = graph.sink.idx;
  } else {
    // init heap with source
    source_idx = graph.source.idx;
  }
  std::priority_queue<Vertex> queue;
  vertices[source_idx].distance = 0;
  queue.push(vertices[source_idx]);
  // run algorithm
  while (!queue.empty()) {
    const Vertex min_vertex = queue.top();
    queue.pop();
    std::vector<AdjVertex> adj_vertices;
    if (reverse) {
      adj_vertices = graph.reversed_adjacency_list[min_vertex.idx];
    } else {
      adj_vertices = graph.adjacency_list[min_vertex.idx];
    }
    for (std::vector<AdjVertex>::const_iterator it = adj_vertices.begin();
         it != adj_vertices.end();
         ++it) {
      // Get edge
      const AdjVertex& adj_vertex  = *it;
      Vertex&          next_vertex = vertices[adj_vertex.vertex.idx];
      //  If there is shorter path to next_vertex through min_vertex.
      if (min_vertex.distance + adj_vertex.weight < next_vertex.distance) {
        // Updating distance of next_vertex
        next_vertex.distance = min_vertex.distance + adj_vertex.weight;
        // std::cout << "Setting vertex " << next_vertex.id << " distance to "
        //           << next_vertex.distance << "\n";
        if (visited.find(next_vertex.idx) == visited.end()) {
          queue.push(next_vertex);
        }
      }
    }
    visited.insert(min_vertex.idx);
  }
  // std::cout << "Shortest path " << reverse << "\n";
  for (int i = 0; i < number_vertices; ++i) {
    // std::cout << "i = " << i << ", id = " << vertices[i].id
    //           << ", d = " << vertices[i].distance << "\n";
    (*lower_bound_weight)[i] = vertices[i].distance;
  }
}

} // namespace bidirectional
