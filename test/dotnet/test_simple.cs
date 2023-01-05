using System;
using System.Collections.Generic;
using Xunit;
using cspy.Dotnet;

public class SimpleTest {
  [Fact]
  public void DoubleVectorTest() {
    List<double> list = new List<double>() {4.0, 20.0};
    DoubleVector double_vector = new DoubleVector(list);
    Assert.Equal(double_vector[0], 4.0);
    Assert.Equal(double_vector[1], 20.0);

    DoubleVector double_vector2 = new DoubleVector(new List<double>() {4.0, 20.0});
    Assert.Equal(double_vector2[0], 4.0);
    Assert.Equal(double_vector2[1], 20.0);
  }

  [Fact]
  public void ConstructTest() {
    DoubleVector max_res = new DoubleVector(new List<double>() {4.0, 20.0});
    DoubleVector min_res = new DoubleVector(new List<double>() {0.0, 0.0});
    int number_vertices = 5;
    int number_edges = 5;
    BiDirectionalCpp alg = new BiDirectionalCpp(number_vertices, number_edges, 0, 4, max_res, min_res);

    // Populate graph
    alg.addNodes(new IntVector(new List<int>() {0, 1, 2, 3, 4}));
    alg.addEdge(0, 1, -1.0, new DoubleVector(new List<double>() {1, 2}));
    alg.addEdge(1, 2, -1.0, new DoubleVector(new List<double>() {1, 0.3}));
    alg.addEdge(2, 3, -10.0, new DoubleVector(new List<double>() {1, 3}));
    alg.addEdge(2, 4, 10.0, new DoubleVector(new List<double>() {1, 2}));
    alg.addEdge(3, 4, -1.0, new DoubleVector(new List<double>() {1, 10}));
    alg.setDirection("forward");

    // Run and query attributes
    alg.run();

    IntVector path = alg.getPath();
    DoubleVector res = alg.getConsumedResources();
    double cost = alg.getTotalCost();

    // Check path
    Assert.Equal(path[0], 0);
    Assert.Equal(path[1], 1);
    Assert.Equal(path[2], 2);
    Assert.Equal(path[3], 3);
    Assert.Equal(path[4], 4);
    // Check final resource
    Assert.Equal(res[0], 4.0);
    Assert.Equal(res[1], 15.3);
    // Check cost
    Assert.Equal(cost, -13.0);
  }

  [Fact]
  public void CallbackTest() {
    DoubleVector max_res = new DoubleVector(new List<double>() {4.0, 20.0});
    DoubleVector min_res = new DoubleVector(new List<double>() {0.0, 0.0});
    int number_vertices = 5;
    int number_edges = 5;
    BiDirectionalCpp alg = new BiDirectionalCpp(number_vertices, number_edges, 0, 4, max_res, min_res);
    MyCallback cb = new MyCallback();

    // Populate graph
    alg.addNodes(new IntVector(new List<int>() {0, 1, 2, 3, 4}));
    alg.addEdge(0, 1, -1.0, new DoubleVector(new List<double>() {1, 2}));
    alg.addEdge(1, 2, -1.0, new DoubleVector(new List<double>() {1, 0.3}));
    alg.addEdge(2, 3, -10.0, new DoubleVector(new List<double>() {1, 3}));
    alg.addEdge(2, 4, 10.0, new DoubleVector(new List<double>() {1, 2}));
    alg.addEdge(3, 4, -1.0, new DoubleVector(new List<double>() {1, 10}));
    alg.setDirection("forward");
    alg.setREFCallback(cb);

    // Run and query attributes
    alg.run();

    IntVector path = alg.getPath();
    DoubleVector res = alg.getConsumedResources();
    double cost = alg.getTotalCost();

    // Check path
    Assert.Equal(path[0], 0);
    Assert.Equal(path[1], 1);
    Assert.Equal(path[2], 2);
    Assert.Equal(path[3], 3);
    Assert.Equal(path[4], 4);
    // Check final resource
    Assert.Equal(res[0], 4.0);
    Assert.Equal(res[1], 15.3);
    // Check cost
    Assert.Equal(cost, -13.0);
  }
}

public class MyCallback : REFCallback {
   public override DoubleVector REF_fwd(DoubleVector cumulative_resource, int tail, int head, DoubleVector edge_resource_consumption, IntVector partial_path, double accummulated_cost)
   {
     Console.WriteLine("CSharpCallback.run()");
     DoubleVector new_res = new DoubleVector();
     new_res.Add(cumulative_resource[0] + edge_resource_consumption[0]);
     new_res.Add(cumulative_resource[1] + edge_resource_consumption[1]);
     return new_res;
   }
}
