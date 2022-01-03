from Graph.Edge import Edge


class Node:
    def __init__(self, _id: int = -1, pos: tuple = None):
        self.id: int = _id
        self.in_edges: dict = {}
        self.out_edges: dict = {}
        self.pos: tuple = pos

        # for GraphAlgo
        self.weight: float = 0
        self.tag: int = 0
        self.info: int = None
        #

    def get_id(self):
        return self.id

    def get_pos(self):
        return self.pos

    def set_weight(self, w: float):
        self.weight = w

    def get_weight(self):
        return self.weight

    def set_tag(self, t: int):
        self.tag = t

    def get_tag(self):
        return self.tag

    def set_info(self, _id: int):
        self.info = _id

    def get_info(self):
        return self.info

    def get_in_edges(self):
        return self.in_edges

    def get_out_edges(self):
        return self.out_edges

    def add_in_edge(self, e: Edge):
        """
        @param e: edge to add
        Adds edge into in_edges
        """
        self.in_edges[e.get_src()] = e

    def add_out_edge(self, e: Edge):
        """
        @param e: edge to add
        Adds edge into out_edges
        """
        self.out_edges[e.get_dst()] = e

    def remove_out_edge(self, dst: int):
        """
        @param dst: index of edge to remove
        removes edge from out_edges
        """
        if dst not in self.out_edges.keys():
            return False
        else:
            del self.out_edges[dst]
            return True

    def remove_in_edge(self, src: int):
        """
        @param src: index of edge to remove
        removes edge from in_edges
        """
        if src not in self.in_edges.keys():
            return False
        else:
            del self.in_edges[src]
            return True

    """
    comparing operators
    """

    def __lt__(self, other):
        return self.weight < other.weight

    def __gt__(self, other):
        return self.weight > other.weight

    def __eq__(self, other):
        return self.weight == other.weight

    def __le__(self, other):
        return self.weight <= other.weight

    def __ge__(self, other):
        return self.weight >= other.weight

    def __ne__(self, other):
        return self.weight != other.weight

    def __repr__(self):
        return f"{self.id}: |edges out| {len(self.out_edges)} |edges in| {len(self.in_edges)}"
