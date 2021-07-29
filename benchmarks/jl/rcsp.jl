"""
Formulate and solve the Beasley and Christofides benchmarks using JuMP
(solved using Gurobi in this case, which seems faster than CPLEX)
"""

using LightGraphs
using JuMP
using Gurobi
using BenchmarkTools # For timing

import Base.parse

"""
Parse a Beasley-Christofides benchmark file and returns
- g - SimpleDiGraph with problem
- min_res - Vector of float with lower bounds
- max_res - Vector of float with upper bounds
- costs - Vector of float with upper bounds
"""
function parse_benchmark(
  filename::String
)::Tuple{
  SimpleDiGraph,Vector{Float64},Vector{Float64},Vector{Float64},AbstractMatrix{Float64}
}
  f = open(filename)
  arc_count = Int(1)
  number_nodes = Int(0)
  number_edges = Int(0)
  number_resources = Int(0)

  for line in eachline(f)
    line = split(line, " ")
    number_nodes, number_edges, number_resources = parse(Int, line[2]),
    parse(Int, line[3]),
    parse(Int, line[4])
    break
  end

  g = SimpleDiGraph(number_nodes)

  min_res = []
  for line in eachline(f)
    line = split(line, " ")
    for r in 1:number_resources
      r = parse(Float64, line[1 + r])
      push!(min_res, r)
    end
    break
  end
  max_res = []
  for line in eachline(f)
    line = split(line, " ")
    for r in 1:number_resources
      r = parse(Float64, line[1 + r])
      push!(max_res, r)
    end
    break
  end
  count = 1
  for line in eachline(f)
    if count == number_nodes
      break
    end
    count += 1
  end
  # Parse edges
  res_costs = zeros(Float64, number_edges, number_resources)
  costs = []
  count = 1
  for line in eachline(f)
    line = split(line, " ")
    i, j, cost = parse(Int, line[2]), parse(Int, line[3]), parse(Float64, line[4])
    if j != 1 || i != number_nodes
      add_edge!(g, i, j)
    end
    push!(costs, cost)
    for r in 1:number_resources
      res = parse(Float64, line[4 + r])
      res_costs[count, r] = res
    end
    count += 1
  end
  close(f)
  return g, min_res, max_res, costs, res_costs
end

function get_result(folder::String, instance_number::Int)::Float64
  f = open("$folder/results.txt")
  count = 1
  result = 0.0
  for line in eachline(f)
    line = split(line, " ")
    if count == instance_number + 1
      result = parse(Int, line[2])
      break
    end
    count += 1
  end
  close(f)
  return result
end

function formulate(
  g::SimpleDiGraph,
  min_res::Vector{Float64},
  max_res::Vector{Float64},
  costs::Vector{Float64},
  res_costs::AbstractMatrix{Float64},
)::Float64
  N = nv(g)
  M = ne(g)
  R = length(max_res)

  model = Model(Gurobi.Optimizer)
  set_silent(model)
  @variable(model, x[e=edges(g)], Bin)
  @constraint(
    model,
    [i = 2:(N - 1)],
    sum(x[Edge(i, j)] for j in outneighbors(g, i)) -
    sum(x[Edge(j, i)] for j in inneighbors(g, i)) == 0
  )
  @constraint(model, sum(x[Edge(1, j)] for j in outneighbors(g, 1)) == 1)
  @constraint(model, -sum(x[Edge(i, N)] for i in inneighbors(g, N)) == -1)
  @constraint(
    model,
    [r = 1:R],
    min_res[r] <=
    sum(res_costs[e_idx, r] * x[e] for (e_idx, e) in enumerate(edges(g))) <=
    max_res[r]
  )

  @objective(model, Min, sum(costs[e_idx] * x[e] for (e_idx, e) in enumerate(edges(g))))
  t = @elapsed optimize!(model)
  @info "$(t*1000)"
  if termination_status(model) == MOI.OPTIMAL
    return objective_value(model)
  end
  return 0.0
end

for i in 1:24
  @info "$i"
  g, min_res, max_res, costs, res_costs = parse_benchmark(
    "../beasley_christofides_1989/rcsp$i.txt"
  )
  obj = formulate(g, min_res, max_res, costs, res_costs)
  opt = get_result("../beasley_christofides_1989/", i)
  if obj != opt
    @error "Failed for instance $i"
  end
end
