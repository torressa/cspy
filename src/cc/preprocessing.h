#ifndef BIDIRECTIONAL_PREPROCESSING_H__
#define BIDIRECTIONAL_PREPROCESSING_H__

#define INF 10000.0

#include "digraph.h"

namespace bidirectional {

/**
 * Solve shortest path and set the lower_bound_weight for each node.
 * Uses LEMON's Bellman-Ford (just in case of negative weights)
 * @see: https://lemon.cs.elte.hu/pub/doc/latest/a00038.html
 *
 * @param[out] lower_bound_weight, vector of double that contains the lower
 * bound in the appropriate vertex index
 * @param[in] graph, @see bidirectional::DiGraph
 * @param[in] forward, bool, whether shortest paths should be found in the
 * forward (Source - Sink) or backward direction (Sink - Source)
 */
void shortest_path(
    std::vector<double>* lower_bound_weight,
    const DiGraph&       graph,
    const bool&          forward);

} // namespace bidirectional

#endif // BIDIRECTIONAL_PREPROCESSING_H__
