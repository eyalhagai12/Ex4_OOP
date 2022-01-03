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
    pokemons_json = client.get_pokemons()
    pokemons = Graph.GraphAlgo.load_poke_from_json(pokemons_json)
    print("Done!")

