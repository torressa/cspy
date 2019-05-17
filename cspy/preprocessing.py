import networkx as nx


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


def prune_graph(G):
    pass


def preprocess(G):
    check_graph(G)
    prune_graph(G)
    return G
