#include <memory>
#include <numeric>
#include <tuple>
#include <vector>

#include "gtest/gtest.h"
#include "src/cc/bidirectional.h"

namespace bidirectional {

class TestVRPyIssue15 : public ::testing::Test {
 protected:
  const bool elementary = true;
};

TEST_F(TestVRPyIssue15, test) {}

} // namespace bidirectional
