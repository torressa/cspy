#ifndef BIDIRECTIONAL_DIGRAPH_H__
#define BIDIRECTIONAL_DIGRAPH_H__

#include <memory>
#include <string>
#include <tuple>
#include <vector>

namespace bidirectional {

/// Data structure for vertices
struct Vertex {
  std::string id;
  int         idx;
  // for use in dijkstra's
  int distance;

  Vertex(){};
  Vertex(const std::string& d, const int& i) : id(d), idx(i){};

  // for use in dijkstra's
  bool operator<(const Vertex& other) const {
    return distance < other.distance;
  }
};

/// Data structure to hold edge attributes.
struct AdjVertex {
  Vertex              vertex;
  double              weight;
  std::vector<double> resource_consumption;
  bool                init = false;

  AdjVertex(){};
  AdjVertex(const Vertex& v, const double& w, const std::vector<double>& r_c)
      : vertex(v), weight(w), resource_consumption(r_c), init(true){};
};

/// Directed graph structure
class DiGraph {
 public:
  int number_vertices;
  int number_edges;
  /// source vertex
  Vertex source;
  /// sink vertex
  Vertex sink;
  /// Vector to keep track of vertices added  to ensure they are not repeated
  std::vector<Vertex> vertices;
  /// Matrix indexed by [tail_vertex.idx][successor_num] and contains the
  /// appropriate edge object if the edge exists in the graph.
  std::vector<std::vector<AdjVertex>> adjacency_list;
  /// same but reversed i.e. [head_vertex.idx][predecessor_num]
  std::vector<std::vector<AdjVertex>> reversed_adjacency_list;
  /// adjacency_matrix to avoid O(E) extraction of edges with the adjacency list
  std::vector<std::vector<std::shared_ptr<AdjVertex>>> adjacency_matrix;

  /**
   * Constructor with memory allocation for vertices, adjacency + reversed list,
   * adjacency matrix.
   *
   * @param[in] number_vertices, int
   * @param[in] number_edges, int
   */
  DiGraph(const int& number_vertices, const int& number_edges);

  /// Add a new edge to the graph. Updates nodes and adjacency_matrix
  void addEdge(
      const std::string&         tail,
      const std::string&         head,
      const double&              weight,
      const std::vector<double>& resource_consumption);
  /// Check whether a (tail, head) edge exists.
  bool checkEdge(const int& tail, const int& head) const;
  /// If a (tail, head) edge exists, retrieves the appropriate edge object
  AdjVertex getAdjVertex(const int& tail, const int& head) const;
  /// initialise reversed_adjacency_list for backward vertex iterations
  void initReversedAdjList();

 private:
  /// whether the source vertex has already been saved in vertices
  bool source_saved_ = false;
  /// whether the sink vertex has already been saved in vertices
  bool sink_saved_ = false;
  ///
  int number_vertices_added_ = 0;
  /**
   * Checks if a vertex with the same id already exists, in which case, it is
   * retrieved and returned.
   * Otherwise, creates a new vertex and `vertices_added_` vector is updated.
   */
  Vertex addVertex(const std::string& id);
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_DIGRAPH_H__
