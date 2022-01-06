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

    client.start()
    # game started:
    while client.is_running() == 'true':

        info = load_info_from_json(client.get_info())  # each round, get the info from the server

        # initialize lists
        # graph_cpy = graph_algo.graph.__copy__()
        temp = load_pokemons_from_json(client.get_pokemons())

        agent_list = load_agents_from_json(client.get_agents())
        # print("agents: {}".format(len(agent_list)))

        # update GUI
        gui.set_pokemons(temp)
        gui.set_agents(agent_list)

        # go over all pokemons
        for pokemon in temp:
            if pokemon not in pokemon_list:
                # add the pokemon to the helper graph as a node
                node_id = max(graph_cpy.get_all_v().keys()) + 1
                pos = pokemon.pos
                poke_value = pokemon.value
                type = pokemon.type
                pokemon.id = node_id
                graph_cpy.add_node(node_id, pos, poke_value, type)

                # find its edge
                tup = graph_algo.graph.find_edge_for_pokemon(pokemon)
                graph_cpy.add_edge(tup[0].src, node_id, tup[1])
                graph_cpy.add_edge(node_id, tup[0].dst, tup[2])
                poke_node = graph_cpy.get_node(node_id)
                poke_node.edge = tup[0]

                # delete the original edge
                try:
                    graph_cpy.remove_edge(tup[0].src, tup[0].dst)
                except Exception as e:
                    print("Edge doesnt exist")

                # add the pokemon to the pokemon list
                pokemon_list.append(poke_node)

        # ~~~~~ GUI ~~~~~ #
        gui.run_gui(info)
        # ~~~~~ GUI ~~~~~ #

        """
        Algorithm part -> when there is only one agent use loop
        else, use threads.
        """
        for pokemon in pokemon_list:
            agent = Utils.best_agent(copy_algo, agent_list, pokemon)
            pokemon.assigned_agent = agent.id

        stop = False

        if len(agent_list) > 1:
            # loop on agent_list in case of multiple agents
            for agent in agent_list:
                Utils.run_agent(agent, copy_algo, client, stop)  # run the agent on its path
        else:
            # use threads for better results in case of one agent
            busy_agents = agent_list
            threads = []
            # create thread for the agent
            for agent in busy_agents:
                thread = Thread(target=Utils.run_agent, args=(agent, copy_algo, client, stop))
                threads.append(thread)
                thread.start()

            i = 0
            # wait for a thread to stop
            while threads[i % len(threads)].is_alive():
                i += 1

            stop = True  # if one thread has finished, kill all remaining threads
            for thread in threads:
                thread.join()

        if gui.stop_button.pressed:  # if the user stopped the game
            client.stop_connection()
            pygame.quit()
            exit(0)

        client.move()
        print(pokemon_list)
