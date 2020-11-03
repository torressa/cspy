#ifndef BIDIRECTIONAL_DIGRAPH_H__
#define BIDIRECTIONAL_DIGRAPH_H__

#include <map>
#include <string>
#include <vector>

namespace bidirectional {

/// Data structure to hold edge attributes.
struct Edge {
  std::string         tail;
  std::string         head;
  double              weight;
  std::vector<double> resource_consumption;
};

/// Directed graph structure
struct DiGraph {
  std::vector<std::string>                          nodes;
  std::vector<Edge>                                 edges;
  std::vector<std::tuple<std::string, std::string>> node_pairs;
};

void addNode(DiGraph* graph, const std::string& node);
void addEdgeToDiGraph(
    DiGraph*                   graph,
    const std::string&         tail,
    const std::string&         head,
    const double&              weight,
    const std::vector<double>& resource_consumption);

/// Check whether an edge (tail, head) is in a graph.
bool checkEdgeInDiGraph(
    const DiGraph&     graph,
    const std::string& tail,
    const std::string& head);

/// Check whether an edge (tail, head) is in a graph.
Edge getEdgeInDiGraph(
    const DiGraph&     graph,
    const std::string& tail,
    const std::string& head);

} // namespace bidirectional

#endif // BIDIRECTIONAL_DIGRAPH_H__
