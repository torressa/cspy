// Simple testing script using Google testing C++ suite.
// (apparently one of the easiest ones to use)

#include "gtest/gtest.h"

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
