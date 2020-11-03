#ifndef TEST_TEST_LABELLING_H__
#define TEST_TEST_LABELLING_H__

#include <memory>

#include "bidirectional.h"
#include "digraph.h"
#include "gtest/gtest.h"
#include "labelling.h"

namespace labelling {

class TestLabelling : public ::testing::Test {
 protected:
  double                   weight  = 10.0;
  std::string              node    = "B";
  std::vector<double>      res     = {6.0, 5.0};
  std::vector<std::string> path    = {"Source"};
  std::vector<double>      max_res = {20.0, 20.0};
  std::vector<double>      min_res = {0.0, 0.0};
};

} // namespace labelling

#endif // TEST_TEST_LABELLING_H__
