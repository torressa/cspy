#include "preprocessing.h"

#include <algorithm>
#include <iostream>
#include <queue>
#include <set>

#include "digraph.h"

namespace bidirectional {

void dijkstra(std::vector<double>* lower_bound_weight, const DiGraph& graph) {
  const int&    number_vertices = graph.number_vertices;
  std::set<int> not_visited;
  // vertices have idx and distance
  std::vector<Vertex> vertices = graph.vertices;
  for (int i = 0; i < number_vertices; ++i) {
    vertices[i].distance = INF;
    not_visited.insert(vertices[i].idx);
  }
  // init heap with source
  const int&                  source_idx = graph.source.idx;
  std::priority_queue<Vertex> queue;
  vertices[source_idx].distance = 0;
  queue.push(vertices[source_idx]);
  // run algorithm
  while (!queue.empty()) {
    const Vertex min_vertex = queue.top();
    queue.pop();
    for (std::set<int>::const_iterator it = not_visited.begin();
         it != not_visited.end();
         ++it) {
      // If edge exists
      if (graph.checkEdge(min_vertex.idx, *it)) {
        // Get edge
        const AdjVertex& adj_vertex =
            *graph.adjacency_matrix[min_vertex.idx][*it];
        Vertex& next_vertex = vertices[adj_vertex.vertex.idx];
        //  If there is shorted path to next_vertex through min_vertex.
        if (next_vertex.distance > min_vertex.distance + adj_vertex.weight) {
          // Updating distance of v
          next_vertex.distance = min_vertex.distance + adj_vertex.weight;
          queue.push(next_vertex);
        }
      }
    }
    not_visited.erase(min_vertex.idx);
  }
  for (int i = 0; i < number_vertices; ++i) {
    (*lower_bound_weight)[i] = vertices[i].distance;
  }
}

} // namespace bidirectional
