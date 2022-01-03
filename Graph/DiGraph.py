import copy
from Graph.GraphInterface import GraphInterface
from Graph.Node import Node
from Graph.Edge import Edge
from Game.Pokemon import Pokemon


class DiGraph(GraphInterface):
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.mc = 0

    def v_size(self):
        """
        Returns the number of vertices in this graph
        @return: The number of vertices in this graph
        """
        return len(self.nodes)

    def e_size(self):
        """
        Returns the number of edges in this graph
        @return: The number of edges in this graph
        """
        return len(self.edges)

    def get_all_v(self):
        """
        return a dictionary of all the nodes in the Graph, each node is represented using a pair:
        (node_id, node_data)
        """
        return self.nodes

    def get_edges(self):
        return self.edges

    def get_node(self, _id: int):
        return self.nodes[_id]

    def get_edge(self, src, dest):
        if dest == src:
            return None

        return self.nodes[src].get_out_edges()[dest]

    def __copy__(self):
        c = DiGraph()
        c.nodes = copy.deepcopy(self.nodes)
        c.edges = copy.deepcopy(self.edges)
        c.mc = copy.deepcopy(self.mc)
        return c

    def all_in_edges_of_node(self, id1: int):
        """
        return a dictionary of all the nodes connected to (into) node_id,
        each node is represented using a pair: (other_node_id, weight)
        """
        out = {}
        for edge in self.nodes[id1].get_in_edges().values():
            out[edge.get_src()] = edge.get_weight()
        return out

    def all_out_edges_of_node(self, id1: int):
        """
        return a dictionary of all the nodes connected from node_id , each node is represented using a pair:
        (other_node_id, weight)
        """
        out = {}
        for edge in self.nodes[id1].get_out_edges().values():
            out[edge.get_dst()] = edge.get_weight()
        return out

    def get_mc(self):
        """
        Returns the current version of this graph,
        on every change in the graph state - the MC should be increased
        @return: The current version of this graph.
        """
        return self.mc

    def add_edge(self, id1: int, id2: int, weight: float):
        """
        Adds an edge to the graph.
        @param id1: The start node of the edge
        @param id2: The end node of the edge
        @param weight: The weight of the edge
        @return: True if the edge was added successfully, False o.w.
        Note: If the edge already exists or one of the nodes dose not exists the functions will do nothing
        """
        if len(self.edges) == 0:
            e = Edge(0, id1, id2, weight)
            self.edges[0] = e
            self.nodes[id1].add_out_edge(e)
            self.nodes[id2].add_in_edge(e)
            self.mc += 1
            return True
        else:
            _id = max(self.edges.keys()) + 1
            e = Edge(_id, id1, id2, weight)
            self.edges[_id] = e
            self.nodes[id1].add_out_edge(e)
            self.nodes[id2].add_in_edge(e)
            self.mc += 1
            return True

    def add_node(self, node_id: int, pos: tuple = None, value=-1, type=1):
        """
        Adds a node to the graph.
        @param node_id: The node ID
        @param pos: The position of the node
        @param value: the value of a pokemon only used when adding a pokemon
        @param type: the edge direction in the graph, only used when adding a pokemon
        @return: True if the node was added successfully, False o.w.
        Note: if the node id already exists the node will not be added
        """
        if node_id in self.nodes.keys():
            return False
        else:
            if value != -1:
                self.nodes[node_id] = Pokemon(node_id, pos, value, type)
            else:
                self.nodes[node_id] = Node(node_id, pos)
            self.mc += 1
            return True

    def remove_node(self, node_id: int):
        """
        Removes a node from the graph.
        @param node_id: The node ID
        @return: True if the node was removed successfully, False o.w.
        Note: if the node id does not exists the function will do nothing
        """
        if node_id not in self.nodes.keys():
            return False
        else:
            temp_in = self.nodes[node_id].get_in_edges()
            temp_out = self.nodes[node_id].get_out_edges()

            temp_in = [edge for edge in temp_in.values()]
            temp_out = [edge for edge in temp_out.values()]

            for edge in temp_in:
                self.remove_edge(edge.get_src(), edge.get_dst())
            for edge in temp_out:
                self.remove_edge(edge.get_src(), edge.get_dst())
            del self.nodes[node_id]
            self.mc += 1
            return True

    def remove_edge(self, node_id1: int, node_id2: int):
        """
        Removes an edge from the graph.
        @param node_id1: The start node of the edge
        @param node_id2: The end node of the edge
        @return: True if the edge was removed successfully, False o.w.
        Note: If such an edge does not exists the function will do nothing
        """
        if node_id1 not in self.nodes.keys() or node_id2 not in self.nodes.keys():
            return False
        else:
            if self.nodes[node_id1].out_edges[node_id2] is not None:
                _id = self.nodes[node_id1].out_edges[node_id2].get_id()
                del self.edges[_id]

                self.nodes[node_id1].remove_out_edge(node_id2)
                self.nodes[node_id2].remove_in_edge(node_id1)

                self.mc += 1
                return True
            return False

    def __repr__(self):
        return f"Graph: |V|={len(self.nodes)} , |E|={len(self.edges)}"
