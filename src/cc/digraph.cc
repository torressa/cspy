#include "digraph.h"

#include <algorithm>
#include <iostream>

namespace bidirectional {

/// Returns an edge struct.
Edge makeEdge(
    const std::string&         tail,
    const std::string&         head,
    const double&              weight,
    const std::vector<double>& resource_consumption) {
  const Edge edge = {tail, head, weight, resource_consumption};
  return edge;
}

void addNode(DiGraph* graph, const std::string& node) {
  graph->nodes.push_back(node);
}

void addEdgeToDiGraph(
    DiGraph*                   graph,
    const std::string&         tail,
    const std::string&         head,
    const double&              weight,
    const std::vector<double>& resource_consumption) {
  addNode(graph, tail);
  addNode(graph, head);
  graph->edges.push_back(makeEdge(tail, head, weight, resource_consumption));
  graph->node_pairs.push_back(std::make_tuple(tail, head));
}

bool checkEdgeInDiGraph(
    const DiGraph&     graph,
    const std::string& tail,
    const std::string& head) {
  return (
      std::find(
          graph.node_pairs.begin(),
          graph.node_pairs.end(),
          std::make_tuple(tail, head)) != graph.node_pairs.end());
}

Edge getEdgeInDiGraph(
    const DiGraph&     graph,
    const std::string& tail,
    const std::string& head) {
  Edge              edge;
  std::vector<Edge> extract_edge;
  std::copy_if(
      graph.edges.begin(),
      graph.edges.end(),
      std::inserter(extract_edge, extract_edge.end()),
      [&tail, &head](const Edge& e) {
        return e.tail == tail && e.head == head;
      });
  if (extract_edge.size() == 1)
    edge = extract_edge[0];
  return edge;
}

} // namespace bidirectional
