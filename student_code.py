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
from Game.GameInfo import load_info_from_json
from Graph.GraphAlgo import GraphAlgo, load_pokemons_from_json, load_agents_from_json

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

    # create info object and add relevant agents
    info = load_info_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":" + str(i) + "}")

    # init GUI
    gui = GUI(graph_algo, [], [], client)

    # this command starts the server - the game is running now
    client.start()
    # game started:
    while client.is_running() == 'true':

        info = load_info_from_json(client.get_info())  # for each loop refresh info

        # initialize graph and lists
        graph_cpy = graph_algo.graph.__copy__()
        pokemon_list = load_pokemons_from_json(client.get_pokemons())
        agent_list = load_agents_from_json(client.get_agents())

        # update GUI
        gui.set_pokemons(pokemon_list)
        gui.set_agents(agent_list)

        for pokemon in pokemon_list:
            idd = max(graph_cpy.get_all_v().keys()) + 1
            graph_cpy.add_node(node_id=idd, pos=pokemon.pos, value=pokemon.value, type=pokemon.type)
            tup = graph_algo.graph.find_edge_for_pokemon(pokemon)
            graph_cpy.add_edge(tup[0].src, idd, tup[1])
            graph_cpy.add_edge(idd, tup[0].dst, tup[2])
            pokemon.edge = tup[0]
            try:
                print(f"edge: source: {tup[0].src}, destination: {tup[0].dst})")
                graph_cpy.remove_edge(tup[0].src, tup[0].dst)
            except Exception as e:
                print("Edge doesnt exist")
                # that doesnt matter since the moves happen on the original graph and it is strongly connected

        # print(graph_cpy)
        copy_algo = GraphAlgo(graph_cpy)

        """ ~~~~~ GUI ~~~~~ """
        gui.run_gui(info)
        """ ~~~~~ GUI ~~~~~ """

        """ Algorithm """
        pokemon_list.sort(reverse=True, key=lambda x: x.value)
        # assign agent for each pokemon
        for pokemon in pokemon_list:
            agent_id = Utils.find_optimal_agent(agent_list, pokemon, copy_algo)
            pokemon.assigned_agent = agent_id

        stop = False  # global variable for threads use

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
        """ Algorithm """

# game over
