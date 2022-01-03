import math
import random

from collections import OrderedDict
from heapq import heappush
from heapq import heappop
from Graph.Node import Node
from Graph.DiGraph import DiGraph


def infinity_weights(graph: DiGraph):
    """
    @param graph
    Sets all graph's nodes' weights to math.inf
    """
    for node in graph.get_all_v().values():
        node.set_weight(math.inf)


def reset_weights(graph: DiGraph):
    """
    @param graph
    Sets all graph's nodes' weights to 0
    """
    for node in graph.get_all_v().values():
        node.set_weight(0)


def reset_tags(graph: DiGraph):
    """
    @param graph
    Sets all graph's nodes' tags to 0
    """
    for node in graph.get_all_v().values():
        node.set_tag(0)


def reset_info(graph: DiGraph):
    """
    @param graph
    Sets all graph's nodes' weights to math.inf
    """
    for node in graph.get_all_v().values():
        node.set_info(None)


def reset_all(graph: DiGraph):
    """
    @param graph
    Sets all graph's nodes' weights, tags, and info to to 0, 0, None
    """
    for node in graph.get_all_v().values():
        node.set_weight(0)
        node.set_tag(0)
        node.set_info(None)


def dijkstra(graph: DiGraph, source: Node):
    """
    @param graph
    @param source: source node
    Computes minimum distance of all nodes from source node
    result is saved into the other node's weight (not the source node)
    """
    heap = []
    infinity_weights(graph)
    source.set_weight(0)
    heappush(heap, source)
    while heap:
        temp = heappop(heap)
        if temp.get_tag() == 1:
            continue
        temp_edges = temp.get_out_edges()
        for edge in temp_edges.values():
            weight = temp.get_weight() + edge.get_weight()
            if weight < graph.get_node(edge.get_dst()).get_weight():
                graph.get_node(edge.get_dst()).set_weight(weight)
                next_node = graph.get_node(edge.get_dst())
                next_node.set_info(temp)  # for shortest path

        for edge in temp_edges.values():
            if graph.get_node(edge.get_dst()).get_tag() != 1:
                next_node = graph.get_node(edge.get_dst())
                heappush(heap, next_node)

        temp.set_tag(1)
    reset_tags(graph)


def find_max_distance(graph: DiGraph, source: Node):
    """
    @param graph
    @param source: source node
    @returns index
    Finds the farthest node from source node and returns its index
    """
    reset_all(graph)
    dijkstra(graph, source)
    max_weight = -math.inf
    index = -1
    for node in graph.get_all_v().values():
        if node.get_weight() > max_weight:
            max_weight = node.get_weight()
            index = node.get_id()
    return index


def threaded_find_max_distance(graph: DiGraph, ids: list, weights: list):
    """
    @param graph
    @param ids: source node
    @param weights: empty list
    Finds the farthest node from source node
    and adds the source's index and farthest node's weight into the list
    """
    res = []
    for idd in ids:
        source = idd
        dijkstra(graph, source)
        max_weight = -math.inf
        for node in graph.get_all_v().values():
            if node.get_weight() > max_weight:
                max_weight = node.get_weight()
        res.append((source, max_weight))
    weights.extend(res)


def make_shortest_list(destination: Node):
    """
    @param destination: last connected node
    @returns x: list that represents the shortest path from a destination's source node to itself
    Creates a list that represents the shortest path from a destination's source node to itself
    """
    x = []
    parent = destination.get_info()
    while parent is not None:
        x.insert(0, parent.get_id())
        parent = parent.get_info()
    if destination.get_weight() is not math.inf:
        x.append(destination.get_id())
    return x


def custom_search(graph: DiGraph, cities: list):
    result = []
    best_node = graph.get_node(cities[0])
    overall_distance = 0

    while best_node is not None:
        reset_all(graph)
        (n, d) = add_closest(graph, best_node, cities, result)
        best_node = n
        if d is not math.inf:
            overall_distance += d
    # temp = result
    # result = list(OrderedDict.fromkeys(result))
    return result, overall_distance


def add_closest(graph: DiGraph, src: Node, cities: list, result: list):
    dijkstra(graph, src)
    min_dist = math.inf
    best_node = None
    for index in cities:
        node = graph.get_node(index)
        if node is not None and node.get_id() is not src.get_id() and node.get_id() not in result:
            if node.get_weight() < min_dist:
                min_dist = node.get_weight()
                best_node = node

    if best_node is not None:
        path = make_shortest_list(best_node)
        result.extend(path)

    return best_node, min_dist


def handle_empty_graph(graph: DiGraph):
    """
    @param: graph
    if a graph is "empty" (nodes without position), generate positions
    and attach them to the relevant nodes
    """
    nodes = list(graph.get_all_v().values())
    node_with_pos = None
    for node in nodes:
        if node.pos:
            node_with_pos = node
            break

    # if no nodes have pos, generate pos for initial node
    if node_with_pos is None:
        nodes[0].pos = (1, 1)
        node_with_pos = nodes[0]

    for node in nodes:
        if not node.pos:
            gen_loc(node, node_with_pos.pos)


def gen_loc(node: Node, loc: tuple):
    """
    @param node
    @param loc
    generate a position to a node using a tuple
    """
    eps = random.uniform(0, 0.3)
    x = random.uniform(loc[0] - eps, loc[0] + eps)
    y = random.uniform(loc[1] - eps, loc[1] + eps)
    node.pos = (x, y)
