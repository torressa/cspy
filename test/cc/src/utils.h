#ifndef TEST_UTILS_H__
#define TEST_UTILS_H__

#include <cmath> // ceil
#include <ctime> // clock_t
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

// File related

// Skip a number of lines in a file
void skipLines(std::ifstream& file, std::string& line, const int& num_lines);

// Load for beasley_christofides benchmarks
void loadMaxMinRes(
    std::vector<double>* max_res,
    std::vector<double>* min_res,
    int*                 num_nodes,
    int*                 num_arcs,
    int*                 num_resources,
    const std::string&   path_to_instance);

// Get benchmark cost for beasley_christofides instance
double getBestCost(const std::string& path_to_data, const int& instance_number);

// Write a row to a file (append as default)
void writeToFile(
    const std::string& output_path,
    const std::string& file_name,
    const std::string& row,
    const bool&        append = true);

// Get elapsed time since start time in milliseconds
int getElapsedTime(const clock_t& start_time);

#endif // TEST_UTILS_H__
