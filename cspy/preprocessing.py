import logging
import networkx as nx


def check_inputs(max_res, min_res, direc_in):
    '''Checks whether inputs are acceptably formated lists'''
    if isinstance(max_res, list) and isinstance(min_res, list):
        if len(max_res) == len(min_res) >= 2:
            if (all(isinstance(item, (float, int)) for item in max_res) and
                    all(isinstance(item, (float, int)) for item in min_res)):
                pass
            else:
                raise Exception("Elements of input lists must be numbers")
        else:
            raise Exception("Input lists have to be equal length >= 2")
    else:
        raise Exception("Inputs have to be lists with length >= 2")
    if direc_in not in ['forward', 'backward', 'both']:
        raise Exception(
            "Input direction has to be 'forward', 'backward', or 'both'")


def check_graph(G):
    '''Checks whether input graph has required properties'''

    def _check_graph_attr():
        '''Checks whether input graph has n_res attribute'''
        if 'n_res' not in G.graph:
            raise Exception("Input graph must have 'n_res' attribute.")

    def _check_edge_attr():
        '''Checks whether edges in input graph have res_cost attribute'''
        if not all('res_cost' in edge[2] for edge in G.edges(data=True)):
            raise Exception(
                "Input graph must have edges with 'res_cost' attribute.")

    def _check_path():
        '''Checks whether a 'Source' -> 'Sink' path exists.
        Also covers nodes missing and other standard networkx exceptions'''
        try:
            nx.has_path(G, 'Source', 'Sink')
        except nx.NetworkXException as e:
            raise Exception("An error occured: {}".format(e))

    errors = []
    # Perform each check
    for check in [_check_graph_attr, _check_edge_attr, _check_path]:
        try:
            check()
        except Exception as e:
            errors.append(e)  # if check fails save error message
    if errors:
        # if any check has failed raise an exception with all the error
        # messages
        raise Exception('\n'.join('{}'.format(item) for item in errors))


def prune_graph(G, max_res, min_res):
    '''Removes nodes that cannot be reached due to resource limits'''

    def _checkResource(r):
        # check resource r's feasibility along a path

        def _get_weight(i, j, attr_dict):
            # returns number to use as weight for the algorithm
            return attr_dict['res_cost'][r]

        # Get paths from source to all other nodes
        length, path = nx.single_source_bellman_ford(
            G, 'Source', weight=_get_weight)
        res_min.append(
            dict(nx.all_pairs_bellman_ford_path_length(G, weight=_get_weight)))
        try:
            # If any path violates the resource upper or lower bounds
            # then, add the problematic node to the dictionary
            nodes_to_remove.update({
                path[key][-2]: val for key, val in length.items()
                if val > max_res[r] or val < min_res[r]})
            # path is a dict of the form:
            # {node_i: [Source, ..., node_k, node_i]}.
            # Hence, if node_i is found to violate a resource constraint, it is
            # because of node_k, therefore, we add path[key][-2] = node_k to
            # the dictionary of nodes to remove.
        except IndexError:  # No nodes violate resource limits
            pass

    nodes_to_remove = {}
    res_min = []
    # Map function for each resource
    list(map(_checkResource, range(0, G.graph['n_res'])))
    if nodes_to_remove:  # if there are nodes to remove
        # Filter out source or sink
        nodes_to_remove = {
            key: val for key, val in nodes_to_remove.items()
            if key != 'Source' or key != 'Sink'}
        G.remove_nodes_from(nodes_to_remove)
        logging.info("Removed {} nodes".format(len(nodes_to_remove)))
    return G, res_min


def preprocess_graph(G, max_res, min_res):
    '''Wrapper'''
    check_graph(G)
    G, res_min = prune_graph(G, max_res, min_res)
    check_graph(G)
    return G, res_min
