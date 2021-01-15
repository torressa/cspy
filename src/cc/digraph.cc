#include "digraph.h"

#include <algorithm> // find_if

namespace bidirectional {

DiGraph::DiGraph(const int& n_v, const int& n_e)
    : number_vertices(n_v), number_edges(n_e) {
  vertices.resize(number_vertices);
  adjacency_list.resize(number_vertices);
  adjacency_matrix.resize(
      number_vertices,
      std::vector<std::shared_ptr<AdjVertex>>(number_vertices, nullptr));
};

Vertex DiGraph::addVertex(const std::string& id) {
  const int idx = number_vertices_added_;
  Vertex    vertex;
  // Check if vertex with matching id already present
  auto it =
      std::find_if(vertices.begin(), vertices.end(), [&id](const Vertex& v) {
        return (v.id == id);
      });
  // vertex doesn't already exist
  if (it == vertices.end()) {
    // fill new vertex attributes
    vertex.idx = idx;
    vertex.id  = id;
    // Add new vertex
    vertices[idx] = vertex;
    ++number_vertices_added_;
  } else {
    // Retrieve existing vertex
    vertex = *it;
  }
  // Save source / sink if appropriate
  if (!source_saved_ && id == "Source") {
    source        = vertex;
    source_saved_ = true;
  } else if (!sink_saved_ && id == "Sink") {
    sink        = vertex;
    sink_saved_ = true;
  }
  return vertex;
}

void DiGraph::addEdge(
    const std::string&         tail,
    const std::string&         head,
    const double&              weight,
    const std::vector<double>& resource_consumption) {
  // Get vertices
  const Vertex& tail_vertex = addVertex(tail);
  const Vertex& head_vertex = addVertex(head);
  // Create edge
  auto adj_vertex_ptr =
      std::make_shared<AdjVertex>(head_vertex, weight, resource_consumption);
  // add to list
  adjacency_list[tail_vertex.idx].push_back(*adj_vertex_ptr);
  // add to matrix as pointer
  adjacency_matrix[tail_vertex.idx][head_vertex.idx].swap(adj_vertex_ptr);
}

bool DiGraph::checkEdge(const int& tail, const int& head) const {
  return (adjacency_matrix[tail][head] != nullptr);
};

AdjVertex DiGraph::getAdjVertex(const int& tail, const int& head) const {
  if (checkEdge(tail, head)) {
    return *adjacency_matrix[tail][head];
  }
  return AdjVertex(); // empty
}

void DiGraph::initReversedAdjList() {
  reversed_adjacency_list.resize(number_vertices);
  for (int i = 0; i < number_vertices; ++i) {
    for (const AdjVertex& adj_vertex : adjacency_list[i]) {
      reversed_adjacency_list[adj_vertex.vertex.idx].emplace_back(
          vertices[i], adj_vertex.weight, adj_vertex.resource_consumption);
    }
  }
}

} // namespace bidirectional
