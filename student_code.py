"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
import sys
import math as mt
import time as tme
from threading import Thread
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


def scale(data, min_screen, max_screen, min_data, max_data):
    """
    get the scaled data with proportions min_data, max_data
    relative to min and max screen dimentions
    """
    return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen


# decorate scale with the correct values
def my_scale(data, x=False, y=False):
    if x:
        return scale(data, 50, screen.get_width() - 50, min_x, max_x)
    if y:
        return scale(data, 50, screen.get_height() - 50, min_y, max_y)


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
    # return the optimal agent's id that has the optimal path to the pokemon from its last destination



if __name__ == '__main__':
    # init pygame
    WIDTH, HEIGHT = 1080, 720

    # default port
    PORT = 6666
    # server host (default localhost 127.0.0.1)
    HOST = '127.0.0.1'
    pygame.init()

    screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
    clock = pygame.time.Clock()
    pygame.font.init()

    client = Client()
    client.start_connection(HOST, PORT)
    graph_json = client.get_graph()
    FONT = pygame.font.SysFont('Arial', 20, bold=True)

    # get data proportions
    min_x = min(list(graph_algo.get_graph().nodes.values().Nodes), key=lambda n: n.pos.x).pos.x
    min_y = min(list(graph_algo.get_graph().nodes.values().Nodes), key=lambda n: n.pos.y).pos.y
    max_x = max(list(graph_algo.get_graph().nodes.values().Nodes), key=lambda n: n.pos.x).pos.x
    max_y = max(list(graph_algo.get_graph().nodes.values().Nodes), key=lambda n: n.pos.y).pos.y

    radius = 15
    # create info object and add agents
    info = load_info_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":" + str(i) + "}")

    # this commnad starts the server - the game is running now
    client.start()

    while client.is_running() == 'true':

        info = load_info_from_json(client.get_info())  # each round, get the info from the server

        # initialize pokemon list
        graph_cpy = graph_algo.graph.__copy__()
        pokemon_list = load_pokemons_from_json(client.get_pokemons())
        agent_list = load_agents_from_json(client.get_agents())
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

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GUI
        # check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
        # refresh surface
        screen.fill(Color(0, 0, 0))

        # draw nodes
        for n in graph_algo.get_graph().nodes.values():
            x = my_scale(n.pos[0], x=True)
            y = my_scale(n.pos[1], y=True)
            # its just to get a nice antialiased circle
            gfxdraw.filled_circle(screen, int(x), int(y),
                                    radius, Color(240, 230, 140))
            gfxdraw.aacircle(screen, int(x), int(y),
                                radius, Color(255, 255, 255))

            # draw the node id
            id_srf = FONT.render(str(n.id), True, Color(0, 0, 0))
            rect = id_srf.get_rect(center=(x, y))
            screen.blit(id_srf, rect)

        # draw edges
        for e in graph_algo.get_graph().edges.values():
            # find the edge nodes
            src = next(n for n in graph_algo.get_graph().nodes.values() if n.id == e.src)
            dest = next(n for n in graph_algo.get_graph().nodes.values() if n.id == e.dst)

            # scaled positions
            src_x = my_scale(src.pos[0], x=True)
            src_y = my_scale(src.pos[1], y=True)
            dest_x = my_scale(dest.pos[0], x=True)
            dest_y = my_scale(dest.pos[1], y=True)

            # draw the line
            pygame.draw.line(screen, Color(51, 161, 201), (src_x, src_y), (dest_x, dest_y))

        # draw agents
        for agent in agent_list:
            x = my_scale(float(agent.pos[0]), x=True)
            y = my_scale(float(agent.pos[1]), y=True)
            pygame.draw.circle(screen, Color(107, 142, 35), (x, y), 10)

        for p in pokemon_list:
            x = my_scale(float(p.pos[0]), x=True)
            y = my_scale(float(p.pos[1]), y=True)
            pygame.draw.circle(screen, Color(255, 128, 0), (x, y), 10)

        # update screen changes
        display.update()

        # refresh rate
        clock.tick(10)

        # choose next edge
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
                
    # game over:


