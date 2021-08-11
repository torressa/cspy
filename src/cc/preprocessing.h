#ifndef BIDIRECTIONAL_PREPROCESSING_H__
#define BIDIRECTIONAL_PREPROCESSING_H__

#define INF 10000.0

#include "digraph.h"

namespace bidirectional {

/**
 * Solve shortest path using the distance provided as input and set the
 * lower_bound_weight for each node.  Uses LEMON's Bellman-Ford (just in case of
 * negative weights)
 * @see: https://lemon.cs.elte.hu/pub/doc/latest/a00038.html
 *
 * @param[out] lower_bound_weight, vector of double that contains the lower
 * bound in the appropriate vertex index
 * @param[in] graph, @see bidirectional::DiGraph
 * @param[in] forward, bool, whether shortest paths should be found in the
 * forward (Source - Sink) or backward direction (Sink - Source)
 */
void lowerBoundWeight(
    std::vector<double>* lower_bound_weight,
    const DiGraph&       graph,
    const bool&          forward);

/**
 * [EXPERIMENTAL] Get possible critical resource by solving longest paths on the
 * graph with each resource as distance for each edge.
 *
 * @param[in] vector of double with maximum resources (upper bounds).
 * @param[in] bidirectional::DiGraph, with graph.
 * @return int with critical resource id.
 */
int getCriticalRes(const std::vector<double>& max_res, const DiGraph& graph);

} // namespace bidirectional

#endif // BIDIRECTIONAL_PREPROCESSING_H__
