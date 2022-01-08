"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
from threading import Thread

import Utils
from GUI import GUI
from Graph.DiGraph import DiGraph
from client import Client
import pygame
from Game.Agent import Agent
from Game.GameInfo import load_info_from_json
from Game.Pokemon import Pokemon
from Graph.GraphAlgo import GraphAlgo, load_pokemons_from_json, load_agents_from_json

DEBUG = True

if __name__ == '__main__':
    # default port
    PORT = 6666
    # server host (default localhost 127.0.0.1)
    HOST = '127.0.0.1'

    client = Client()
    client.start_connection(HOST, PORT)

    # load the json string
    graph_algo = GraphAlgo(DiGraph())
    graph_algo.load_from_json(client.get_graph())

    # create graph copy
    graph_cpy = graph_algo.graph.__copy__()
    copy_algo = GraphAlgo(graph_cpy)

    # create am info object and add as needed agents
    info = load_info_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":" + str(i) + "}")

    # init GUI
    if not DEBUG:
        gui = GUI(graph_algo, [], [], client)
    else:
        gui = GUI(copy_algo, [], [], client)

    # this command starts the server - the game is running now
    pokemon_list = []
    prev_temp = []
    agents = []
    new_pokemons = False
    clock = pygame.time.Clock()

    client.start()
    # game started:
    while client.is_running() == 'true':
        clock.tick(15)
        info = load_info_from_json(client.get_info())  # each round, get the info from the server

        # initialize lists
        # graph_cpy = graph_algo.graph.__copy__()
        temp = load_pokemons_from_json(client.get_pokemons())

        agent_list = load_agents_from_json(client.get_agents())
        # for agent in agent_list:
        #     print(agent)

        if prev_temp != temp:
            prev_temp = temp
            new_pokemons = True

        # add pokemons as nodes to the graph
        if new_pokemons:
            pokemon_list = []
            for pokemon in temp:
                # add pokemon to the graph
                node_id = max(graph_cpy.nodes.keys()) + 1
                graph_cpy.add_node(node_id, pokemon.pos, pokemon.value, pokemon.type)

                # get pokemon and find the edge that it is sitting on
                new_p = graph_cpy.get_node(node_id)
                pokemon_edge, w_to, w_from = graph_algo.graph.find_edge_for_pokemon(new_p)
                new_p.edge = pokemon_edge
                pokemon_list.append(new_p)

                # modify graph
                graph_cpy.add_edge(pokemon_edge.src, node_id, w_to)
                graph_cpy.add_edge(node_id, pokemon_edge.dst, w_from)

                try:
                    graph_cpy.remove_edge(pokemon_edge.src, pokemon_edge.dst)
                except:
                    print("Edge doesnt exist")

        # update GUI
        gui.set_pokemons(pokemon_list)
        gui.set_agents(agent_list)

        # ~~~~~ GUI ~~~~~ #
        gui.run_gui(info)
        # ~~~~~ GUI ~~~~~ #

        """
        Algorithm part -> when there is only one agent use loop
        else, use threads.
        """

        if new_pokemons:
            new_pokemons = False

            # remake all lists and calculations
            agents = agent_list

            # assign each pokemon to an agent
            for pokemon in pokemon_list:
                if pokemon.assigned_agent == -1:
                    agent = Utils.best_agent(copy_algo, agents, pokemon)
                    pokemon.assigned_agent = agent.id

        else:
            # reposition and update agents
            for idx, agent in enumerate(agent_list):
                agents[idx].pos = agent.pos
                agents[idx].speed = agent.speed
                agents[idx].value = agent.value
                agents[idx].dest = agent.dest

        # move agents
        for agent in agents:
            Utils.move_agent(copy_algo, agent, client)

        client.move()
