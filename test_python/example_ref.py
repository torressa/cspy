from random import randint
from numpy import array
from networkx import DiGraph

from cspy import BiDirectional, REFCallback

# import pyBiDirectionalCpp as bd


class Callback(REFCallback):

    def REF_fwd(self, cumul_res, tail, head, edge_res, partial_path,
                cumul_cost):
        print(cumul_res, tail, head, edge_res, partial_path, cumul_cost)
        new_res = cumul_res + edge_res
        return new_res


def main():
    max_res, min_res = [4, 20], [0, 0]
    # Create simple digraph with appropriate attributes
    # No resource costs required for custom REFs
    G = DiGraph(directed=True, n_res=2)
    G.add_edge("Source", "A", res_cost=array([1, 2]), weight=0)
    G.add_edge("A", "Sink", res_cost=array([1, 10]), weight=0)

    callback = Callback()
    bidirectional_cpp = BiDirectional(G,
                                      max_res,
                                      min_res,
                                      REF_callback=callback)


if __name__ == "__main__":
    main()
