import json


def load_info_from_json(file) -> 'GameInfo':
    """
    this method creates the game info from json file
    """
    dictt = json.loads(file)
    dictt = dictt.get("GameServer")
    id = int(dictt.get("id"))
    moves = int(dictt.get("moves"))
    grade = int(dictt.get("grade"))
    game_level = int(dictt.get("game_level"))
    max_user_level = int(dictt.get("max_user_level"))
    pokemons = int(dictt.get("pokemons"))
    agents = int(dictt.get("agents"))
    is_logged_in = bool(dictt.get("is_logged_in"))
    graph = str(dictt.get("graph"))
    return GameInfo(id, moves, grade, game_level, max_user_level, pokemons, agents, is_logged_in, graph)


class GameInfo:

    def __init__(self, id: int, moves: int, grade: int, game_level: int, max_user_level: int, pokemons: int,
                 agents: int, is_logged_in: bool,
                 graph: str):
        self.id = id
        self.moves = moves
        self.grade = grade
        self.game_level = game_level
        self.max_user_level = max_user_level
        self.pokemons = pokemons
        self.agents = agents
        self.is_logged_in = is_logged_in
        self.graph = graph

    def get_id(self):
        return self.id

    def get_moves(self):
        return self.moves

    def get_game_level(self):
        return self.game_level

    def get_max_user_level(self):
        return self.max_user_level

    def get_pokemons(self):
        return self.pokemons

    def get_agents(self):
        return self.agents

    def get_is_logged_in(self):
        return self.is_logged_in

    def get_graph(self):
        return self.graph

    def toStr(self):
        return f"{self.id}, {self.is_logged_in}, {self.game_level}, {self.max_user_level}, {self.graph}, {self.pokemons}, {self.agents}, {self.moves}, {self.grade}"
