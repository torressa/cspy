#ifndef BIDIRECTIONAL_DIGRAPH_H__
#define BIDIRECTIONAL_DIGRAPH_H__

#include <memory>
#include <vector>

#include "lemon/smart_graph.h" // SmartDigraph

// Type defs for LEMON
typedef lemon::SmartDigraph       LemonGraph;
typedef lemon::SmartDigraph::Node LemonNode;
typedef lemon::SmartDigraph::Arc  LemonArc;

namespace bidirectional {

/// Vertex to hold lemon id in the graph and the corresponding user id (may be
/// different)
struct Vertex {
  int lemon_id;
  int user_id;
};

/**
 * Data structure to hold adjacent vertex attributes.
 * (this way it can be used both forward and backward directions)
 */
struct AdjVertex {
  /// Tail/head vertex
  Vertex vertex;
  /// Double with weight/cost for the arc
  double weight;
  /// Vector of doubles with resource consumption
  std::vector<double> resource_consumption;
  /// Bool to check initialisation of the struct
  bool init = false;

  /// Dummy constructor
  AdjVertex(){};
  /// Default constructor
  AdjVertex(const Vertex& v, const double& w, const std::vector<double>& r_c)
      : vertex(v), weight(w), resource_consumption(r_c), init(true){};
  /// Default destructor
  ~AdjVertex(){};
};

/**
 * Directed graph wrapper to create and query a lemon::SmartDigraph.
 * @see: https://lemon.cs.elte.hu/trac/lemon
 */
class DiGraph {
 public:
  /// int. Number of nodes/vertices in the graph.
  int number_vertices;
  /// int. Number of arcs/edges in the graph.
  int                                                      number_edges;
  Vertex                                                   source;
  Vertex                                                   sink;
  std::unique_ptr<LemonGraph>                              lemon_graph_ptr;
  std::unique_ptr<LemonGraph::ArcMap<double>>              weight_map_ptr;
  std::unique_ptr<LemonGraph::ArcMap<std::vector<double>>> res_map_ptr;
  std::vector<Vertex>                                      vertices;

  /**
   * Constructor.
   * Allocates memory for the number of nodes/arcs (uses LEMON allocators) and
   * saves source/sink user ids.
   *
   * @param[in] num_nodes_in, int. Number of nodes in the graph.
   * @param[in] num_arcs_in, int. Number of arcs in the graph.
   * @param[in] source_id_in, int. User id for source node.
   * @param[in] sink_id_in, int. User id for sink node.
   */
  DiGraph(
      const int& num_nodes_in,
      const int& num_arcs_in,
      const int& source_id_in,
      const int& sink_id_in);

  /* Graph Construction */

  /**
   * Add nodes to LEMON SmartDigraph.
   *
   * @param[in] user_nodes, vector of int. Array with user nodes
   */
  void addNodes(const std::vector<int>& user_nodes);

  /**
   * Add arcs to LEMON SmartDigraph.
   *
   * @param[in] tail, int. User id for tail node.
   * @param[in] head, int. User id for head node.
   * @param[in] weight, double. Arc weight/cost.
   * @param[in] resource_consumption, vector of double. Array with consumption
   * of resources for this arc. Optional (may be empty if custom REFs are
   * defined).
   */
  void addEdge(
      const int&                 tail,
      const int&                 head,
      const double&              weight,
      const std::vector<double>& resource_consumption);

  /* Graph Querying */

  /**
   * Extract head node for a given arc.
   *
   * @param[in] arc, lemon::SmartDigraph::Arc.
   * @returns lemon::SmartDigraph::Node with head of arc
   */
  LemonNode head(const LemonArc& arc) const {
    return lemon_graph_ptr->target(arc);
  }

  /**
   * Extract tail node for a given arc.
   *
   * @param[in] arc, lemon::SmartDigraph::Arc.
   * @returns lemon::SmartDigraph::Node with tail of arc
   */
  LemonNode tail(const LemonArc& arc) const {
    return lemon_graph_ptr->source(arc);
  }

  /**
   * Extract lemon id for a given node
   *
   * @param[in] arc, lemon::SmartDigraph::Arc.
   * @param[in] forward, bool. Whether arc is checked forward or not (backward).
   * @returns AdjVertex with arc information
   */
  AdjVertex getAdjVertex(const LemonArc& arc, const bool& forward) const;

  /**
   * Extract lemon node from a given lemon id
   *
   * @param[in] id, lemon::SmartDigraph::Arc.
   * @returns lemon::SmartDigraph::Node corresponding to the lemon id
   */
  LemonNode getLNodeFromId(const int& id) const {
    return lemon_graph_ptr->nodeFromId(id);
  }

  /**
   * Extract lemon id from a given user id
   *
   * @param[in] user_id, int.
   * @returns int with lemon id
   */
  int getNodeIdFromUserId(const int& user_id) const;

  /**
   * Extract lemon id for a given node
   *
   * @param[in] node, lemon::SmartDigraph::Node.
   * @returns Vertex corresponding to the lemon node
   */
  Vertex getVertexFromLNode(const LemonNode& node) const {
    return vertices.at(getId(node));
  }

  /**
   * Extract arc weight from arc map
   *
   * @param[in] arc, lemon::SmartDigraph::Arc.
   * @returns double with arc weight
   */
  double getWeight(const LemonArc& arc) const { return (*weight_map_ptr)[arc]; }

  /**
   * Extract lemon id for a given arc
   *
   * @param[in] arc, lemon::SmartDigraph::Arc.
   * @returns int with lemon id for the arc
   */
  int getId(const LemonArc& arc) const { return lemon_graph_ptr->id(arc); }

  /**
   * Extract lemon id for a given node
   *
   * @param[in] node, lemon::SmartDigraph::Node.
   * @returns int with lemon id for then node
   */
  int getId(const LemonNode& node) const { return lemon_graph_ptr->id(node); }

 private:
  /// int. User id corresponding to the source_node in the graph.
  int source_id_;
  /// int. User id corresponding to the sink node in the graph.
  int sink_id_;

  /**
   * Extract arc resource consumption from arc map
   *
   * @param[in] arc, lemon::SmartDigraph::Arc.
   * @returns vector of double with arc resource consumption
   */
  std::vector<double> getRes(const LemonArc& arc) const {
    return (*res_map_ptr)[arc];
  }

  /**
   * Extract lemon node from a given lemon id
   *
   * @param[in] id, lemon::SmartDigraph::Arc.
   * @returns lemon::SmartDigraph::Node corresponding to the lemon id
   */
  LemonNode getLNodeFromUserId(const int& user_id) const {
    return lemon_graph_ptr->nodeFromId(getNodeIdFromUserId(user_id));
  }
};

} // namespace bidirectional

#endif // BIDIRECTIONAL_DIGRAPH_H__
