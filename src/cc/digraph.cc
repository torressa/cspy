#include "digraph.h"

#include <algorithm> // find_if

namespace bidirectional {

DiGraph::DiGraph(
    const int& num_nodes_in,
    const int& num_arcs_in,
    const int& source_id_in,
    const int& sink_id_in)
    : number_vertices(num_nodes_in),
      number_edges(num_arcs_in),
      lemon_graph_ptr(std::make_unique<LemonGraph>()),
      negative_cost_cycle_present(FALSE),
      weight_map_ptr(
          std::make_unique<LemonGraph::ArcMap<double>>(*lemon_graph_ptr)),
      res_map_ptr(std::make_unique<LemonGraph::ArcMap<std::vector<double>>>(
          *lemon_graph_ptr)),
      source_id_(source_id_in),
      sink_id_(sink_id_in) {
  lemon_graph_ptr->reserveNode(num_nodes_in);
  lemon_graph_ptr->reserveArc(num_arcs_in);
  vertices.resize(num_nodes_in);
}

void DiGraph::addNodes(const std::vector<int>& user_nodes) {
  int  count        = 0;
  bool source_saved = false, sink_saved = false;
  for (const int& user_node : user_nodes) {
    lemon_graph_ptr->addNode();
    // Create and save vertex (lemon id is just count)
    const Vertex new_vertex = {count, user_node};
    vertices[count]         = new_vertex;
    // Save source/sink
    if (!source_saved && user_node == source_id_) {
      source       = new_vertex;
      source_saved = true;
    } else if (!sink_saved && user_node == sink_id_) {
      sink       = new_vertex;
      sink_saved = true;
    }
    ++count;
  }
}

void DiGraph::addEdge(
    const int&                 tail,
    const int&                 head,
    const double&              weight,
    const std::vector<double>& resource_consumption) {
  // Get vertices
  const LemonNode& tail_lnode = getLNodeFromUserId(tail);
  const LemonNode& head_lnode = getLNodeFromUserId(head);
  const LemonArc&  arc        = lemon_graph_ptr->addArc(tail_lnode, head_lnode);
  (*weight_map_ptr)[arc]      = weight;
  (*res_map_ptr)[arc]         = resource_consumption;
  if (weight < 0)
    negative_cost_cycle_present = UNKNOWN;
  all_resources_positive = std::all_of(
      resource_consumption.cbegin(),
      resource_consumption.cend(),
      [](const double& v) { return (v >= 0); });
}

AdjVertex DiGraph::getAdjVertex(const LemonArc& arc, const bool& forward)
    const {
  LemonNode node;
  if (forward) {
    node = head(arc);
  } else {
    node = tail(arc);
  }
  const Vertex&              vertex               = getVertexFromLNode(node);
  const double&              weight               = getWeight(arc);
  const std::vector<double>& resource_consumption = getRes(arc);
  return AdjVertex(vertex, weight, resource_consumption);
}

/// For conversion between user node labels and LemonGraph internal
int DiGraph::getNodeIdFromUserId(const int& user_id) const {
  auto it = std::find_if(
      vertices.begin(), vertices.end(), [&user_id](const Vertex& v) {
        return (v.user_id == user_id);
      });
  return it->lemon_id;
}

} // namespace bidirectional
