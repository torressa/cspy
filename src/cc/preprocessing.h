#ifndef BIDIRECTIONAL_PREPROCESSING_H__
#define BIDIRECTIONAL_PREPROCESSING_H__

#define INF 10000.0

#include "digraph.h"

namespace bidirectional {

/**
 * Run Dijkstra's and set the lower_bound_weight for each node.
 * (not quite dijkstra, as it has a check to make sure it doesn't get stuck)
 *
 * @param[out] lower_bound_weight, vector of double that contains the lower
 * bound in the appropriate vertex index
 */
void dijkstra(
    std::vector<double>* lower_bound_weight,
    const DiGraph&       graph,
    const double&        reverse);

} // namespace bidirectional

#endif // BIDIRECTIONAL_PREPROCESSING_H__
