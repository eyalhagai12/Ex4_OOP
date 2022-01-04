from Game.GameInfo import GameInfo, load_from_json
from client import Client
from Graph.GraphAlgo import GraphAlgo
import Graph.GraphAlgo
from Graph.DiGraph import DiGraph
import json

if __name__ == '__main__':
    client = Client()
    client.start_connection("127.0.0.1", 6666)
    graph_json = client.get_graph()
    graph_algo = GraphAlgo(DiGraph())
    graph_algo.load_from_json(graph_json)
    info = load_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":0}")
    agents = Graph.GraphAlgo.load_agents_from_json(client.get_agents())
    pokemons = Graph.GraphAlgo.load_pokemons_from_json(client.get_pokemons())
    print("Done!")

