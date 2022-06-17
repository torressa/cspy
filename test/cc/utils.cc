#include "gtest/gtest.h"

// cspy
#include "test/cc/utils.h"

void skipLines(std::ifstream& file, std::string& line, const int& num_lines) {
  for (int i = 0; i < num_lines; ++i) {
    std::getline(file, line);
  }
}

void loadMaxMinRes(
    std::vector<double>* max_res,
    std::vector<double>* min_res,
    int*                 num_nodes,
    int*                 num_arcs,
    int*                 num_resources,
    const std::string&   path_to_instance,
    const bool&          forward) {
  std::ifstream      instance_file(path_to_instance);
  std::istringstream iss;
  std::string        line;

  std::getline(instance_file, line);
  iss.str(line);
  iss >> *num_nodes >> *num_arcs >> *num_resources;

  // if (forward) {
  max_res->resize(*num_resources);
  min_res->resize(*num_resources);
  // } else {
  //   max_res->resize(*num_resources + 1);
  //   min_res->resize(*num_resources + 1);
  // }

  std::getline(instance_file, line);
  iss.clear();
  iss.str(line);
  // if (forward) {
  for (int i = 0; i < *num_resources; ++i) {
    iss >> (*min_res)[i];
  }
  // } else {
  //   (*min_res)[0] = 0.0;
  //   for (int i = 1; i < *num_resources + 1; ++i) {
  //     iss >> (*min_res)[i];
  //   }
  // }
  std::getline(instance_file, line);
  iss.clear();
  iss.str(line);
  // if (forward) {
  for (int i = 0; i < *num_resources; ++i) {
    iss >> (*max_res)[i];
  }
  // } else {
  //   (*max_res)[0] = *num_nodes;
  //   for (int i = 1; i < *num_resources + 1; ++i) {
  //     iss >> (*max_res)[i];
  //   }
  // }
  instance_file.close();
}

double getBestCost(
    const std::string& path_to_data,
    const int&         instance_number) {
  const std::string& path_to_results = path_to_data + "results.txt";
  std::ifstream      results_file(path_to_results);
  std::istringstream iss;
  std::string        line;
  double             best_cost;
  int                instance_number_;

  skipLines(results_file, line, instance_number);
  std::getline(results_file, line);
  iss.str(line);
  iss >> instance_number_ >> best_cost;
  return best_cost;
}

void writeToFile(
    const std::string& output_path,
    const std::string& file_name,
    const std::string& row,
    const bool&        append) {
  if (!output_path.empty()) {
    std::ofstream outfile;
    std::string   output_path_to_file = output_path + file_name;
    if (append) {
      outfile.open(output_path_to_file, std::ios_base::app);
    } else {
      outfile.open(output_path_to_file, std::ios_base::trunc);
    }
    outfile << row << "\n";
    outfile.close();
  }
}

int getElapsedTime(const clock_t& start_time) {
  const clock_t timediff    = clock() - start_time;
  const double  timediff_ms = ((double)timediff) / 1000.0;
  return std::ceil(timediff_ms);
}

void checkResult(
    const bidirectional::BiDirectional& alg,
    const std::vector<int>&             path,
    const std::vector<double>&          consumed_resources,
    const double&                       cost) {
  std::string s;
  s += "weight = " + std::to_string(alg.getTotalCost());
  s += ", partial_path=[";
  for (const auto& n : alg.getPath())
    s += std::to_string(n) + ",";
  s += "], res=[";
  for (const auto& r : alg.getConsumedResources())
    s += std::to_string(r) + ",";
  s += "]\n";
  std::cout << s;
  ASSERT_EQ(alg.getPath(), path);
  ASSERT_EQ(alg.getConsumedResources(), consumed_resources);
  ASSERT_EQ(alg.getTotalCost(), cost);
}
