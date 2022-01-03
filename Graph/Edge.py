class Edge:
    def __init__(self, _id: int = -1, src: int = 0, dst: int = 0, w: float = 0):
        self.id = _id
        self.src = src
        self.dst = dst
        self.weight = w

    def get_id(self):
        return self.id

    def get_src(self):
        return self.src

    def get_dst(self):
        return self.dst

    def get_weight(self):
        return self.weight
