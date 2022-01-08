class Agent:
    def __init__(self, _id, value, src, dest, speed, pos):
        self.id = _id
        self.value = value
        self.src = src
        self.dest = dest
        self.speed = speed
        self.pos = pos
        self.path = []
        self.first_time = True

    def __str__(self):
        return "Agent: {}\n\tvalue: {}\n\tspeed: {}\n\tposition: {}\n\tsource: {}\n\tdestination: {}\n\tpath: {}\n\t".format(
            self.id, self.value, self.speed, self.pos, self.src, self.dest, self.path)

    def is_free(self):
        return len(self.path) <= 0
