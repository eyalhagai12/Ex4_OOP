import math
import math as mt

from Game.Agent import Agent
from Game.Pokemon import Pokemon
from Graph.GraphAlgo import GraphAlgo
from Graph.Node import Node
from client import Client


def move_agent(algo: GraphAlgo, agent, client):
    if len(agent.path) > 0 and agent.dest == -1:
        agent.src = agent.dest
        agent.dest = agent.path.pop(0)
        next_node = algo.graph.get_node(agent.dest)

        if isinstance(next_node, Pokemon):
            for key in next_node.out_edges.keys():
                agent.dest = key
                break

        command = '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(agent.dest) + '}'
        print(command)
        client.choose_next_edge(command)


def closest_pokemon(algo: GraphAlgo, agent, pokemon_list: list):
    """
    Find the closest pokemon to a given agent
    """
    pokemon_list.sort(key=lambda x: x.value, reverse=True)
    min_weight = math.inf
    c_pokemon = None
    best_path = []

    # loop over all pokemons and find the closest
    for pokemon in pokemon_list:
        if pokemon.assigned_agent == -1 or pokemon.assigned_agent == agent.id:
            weight, path = algo.shortest_path(agent.src, pokemon.edge.src)
            edge_weight = pokemon.edge.weight
            path.append(algo.graph.get_node(pokemon.edge.dst).id)

            total_weight = (weight + edge_weight) / pokemon.value

            if total_weight < min_weight:
                c_pokemon = pokemon
                min_weight = total_weight
                best_path = path

    if c_pokemon:
        best_path.pop(0)
        c_pokemon.assigned_agent = agent.id
        agent.path = best_path

    return c_pokemon
