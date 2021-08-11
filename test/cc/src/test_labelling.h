#ifndef TEST_TEST_LABELLING_H__
#define TEST_TEST_LABELLING_H__

#include "bidirectional.h"
#include "digraph.h"
#include "gtest/gtest.h"
#include "labelling.h"

namespace labelling {

class TestLabelling : public ::testing::Test {
 protected:
  double                                 weight     = 10.0;
  bidirectional::Vertex                  node       = {1, 1}; // B
  bidirectional::Vertex                  other_node = {2, 2}; // C
  std::vector<double>                    res        = {6.0, 5.0};
  std::vector<int>                       path       = {0};
  std::vector<double>                    max_res    = {20.0, 20.0};
  std::vector<double>                    min_res    = {0.0, 0.0};
  std::unique_ptr<bidirectional::Params> params_ptr =
      std::make_unique<bidirectional::Params>();
};

} // namespace labelling

#endif // TEST_TEST_LABELLING_H__
