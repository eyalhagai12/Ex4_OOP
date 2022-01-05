"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
import sys
import math as mt
import time as tme
from threading import Thread

from GUI import GUI
from Graph.DiGraph import DiGraph
from client import Client
from pygame import gfxdraw
import pygame
from pygame import *
from Game.Agent import Agent
from Game.GameInfo import load_info_from_json
from Game.Pokemon import Pokemon
from Graph.GraphAlgo import GraphAlgo, load_pokemons_from_json, load_agents_from_json
from Graph.Button import Button


def run_agent(agent: Agent, g_algo: GraphAlgo):
    while len(agent.path) != 0:
        p = agent.path[0]
        if stop:  # global bool variable indicate when one pokemon found
            return
        client.choose_next_edge(
            '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(agent.path[1 % len(agent.path)]) + '}')
        agent.pos = g_algo.get_graph().nodes[agent.path[1 % len(agent.path)]].pos
        agent.path.remove(agent.path[0])
        if isinstance(g_algo.get_graph().get_all_v()[p], Pokemon):
            client.move()
            return


def find_optimal_agent(agent_list: list, pokemon: Pokemon, graph: GraphAlgo) -> int:
    free = []
    min_weight = mt.inf
    path = []
    optimal = None

    # find free agents
    for agent in agent_list:
        if len(agent.path) == 0:
            free.append(agent)  # add to the list of free agents

    if len(free) != 0:  # in case we found free agents
        for agent in free:  # loop over the free agents
            weight, temppath = graph.shortest_path(agent.src,
                                                   pokemon.edge.src)  # find the shortest path from agent src to pokemon
            weight1, temppath1 = graph.shortest_path(pokemon.edge.src, pokemon.edge.dst)
            weight += weight1
            temppath += temppath1
            # in case we found an agent with shorter path, switch
            if weight < min_weight:
                min_weight = weight
                path = temppath
                optimal = agent

        optimal.path = path  # update agent path
        print(optimal.path)
        return optimal.id  # return agent id

    else:  # if all are busy, loop over the agents

        for agent in agent_list:
            # in case one of the agents already going to the pokemon node, allocate the same agent
            if pokemon.edge.src in agent.path and pokemon.edge.dst in agent.path:
                return agent.id
            # find the shortest path from the agent last destination to the pokemon
            weight, temppath = graph.shortest_path(agent.path[-1], pokemon.edge.src)
            weight1, temppath1 = graph.shortest_path(pokemon.edge.src, pokemon.edge.dst)
            weight += weight1
            temppath += temppath1
            # in case we found an agent with shorter path, switch
            if weight < min_weight:
                min_weight = weight
                path = temppath
                optimal = agent

        optimal.path += path  # update the agent path
        print(optimal.path)
        return optimal.id


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

    # create am info object and add as needed agents
    info = load_info_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":" + str(i) + "}")

    # init GUI
    gui = GUI(graph_algo, [], [], client)

    # this command starts the server - the game is running now
    client.start()
    # game started:
    while client.is_running() == 'true':

        info = load_info_from_json(client.get_info())  # each round, get the info from the server

        # initialize lists
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
                print("Wtf")

        # print(graph_cpy)
        copy_algo = GraphAlgo(graph_cpy)

        # ~~~~~ GUI ~~~~~ #
        gui.run_gui(info)
        # ~~~~~ GUI ~~~~~ #

        """
        Algorithm part -> when there is only one agent use thread
        else, use for loop.
        """
        pokemon_list.sort(reverse=True, key=lambda x: x.value)
        # assign agent for each pokemon
        for pokemon in pokemon_list:
            # finds an agent for the pokemon
            agent_id: int = find_optimal_agent(agent_list, pokemon, copy_algo)
            pokemon.assigned_agent = agent_id

        stop = False  # global variable, used in threads

        # check the number of agents
        if len(agent_list) > 1:
            # loop between the agents in case of multiple agents
            for agent in agent_list:
                run_agent(agent, copy_algo)  # run the agent on its path
        else:
            # use a thread for better results in case of one agent
            busy_agents = agent_list
            threads = []
            # create thread for the agent
            for agent in busy_agents:
                thread = Thread(target=run_agent, args=(agent, copy_algo))
                threads.append(thread)
                thread.start()

            i = 0
            # loop until the thread stopped
            while threads[i % len(threads)].is_alive():
                i += 1

            stop = True  # if the thread stopped
            for thread in threads:
                thread.join()

        if gui.stop_button.pressed:  # check if the client has stopped the game
            client.stop_connection()
            pygame.quit()
            exit(0)

        print(pokemon_list)

# game over
