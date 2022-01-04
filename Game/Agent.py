

class Agent:
    def __init__(self, _id, value, src, dest, speed, pos):
        self.id = _id
        self.value = value
        self.src = src
        self.dest = dest
        self.speed = speed
        self.pos = pos
        self.path = None
