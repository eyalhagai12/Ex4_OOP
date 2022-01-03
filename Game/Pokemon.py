from Graph.Node import Node


class Pokemon(Node):
    def __init__(self, id=-1, pos=None, value=-1, type=1):
        super().__init__(id, pos)
        self.value = value
        self.type = type
