#include "search.h"

namespace bidirectional {

Search::Search(const Directions& direction_in)
    : direction(direction_in),
      lower_bound_weight(std::make_unique<std::vector<double>>()),
      unprocessed_labels(std::make_unique<std::vector<labelling::Label>>()){};

void Search::makeHeap() {
  if (direction == FWD) {
    // Min-heap
    std::make_heap(
        unprocessed_labels->begin(),
        unprocessed_labels->end(),
        std::greater<>{});
  } else {
    // Max-heap
    std::make_heap(unprocessed_labels->begin(), unprocessed_labels->end());
  }
}

void Search::pushHeap() {
  if (unprocessed_labels->size() > 1) {
    if (direction == FWD) {
      // Min-heap
      std::push_heap(
          unprocessed_labels->begin(),
          unprocessed_labels->end(),
          std::greater<>{});
    } else {
      // Max-heap
      std::push_heap(unprocessed_labels->begin(), unprocessed_labels->end());
    }
  }
}
} // namespace bidirectional
