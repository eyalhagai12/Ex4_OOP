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

    # load the json string
    graph_algo = GraphAlgo(DiGraph())
    graph_algo.load_from_json(client.get_graph())

    # get data proportions
    min_x = min(list(graph_algo.get_graph().nodes.values()), key=lambda n: n.pos[0]).pos[0]
    min_y = min(list(graph_algo.get_graph().nodes.values()), key=lambda n: n.pos[1]).pos[1]
    max_x = max(list(graph_algo.get_graph().nodes.values()), key=lambda n: n.pos[0]).pos[0]
    max_y = max(list(graph_algo.get_graph().nodes.values()), key=lambda n: n.pos[1]).pos[1]

    radius = 15
    # create am info object and add as needed agents
    info = load_info_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":" + str(i) + "}")

    # this command starts the server - the game is running now
    client.start()

    # game started:
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
                                    radius, Color(64, 80, 174))
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
            pygame.draw.line(screen, Color(61, 72, 126),
                                (src_x, src_y), (dest_x, dest_y))

        # draw agents
        for agent in agent_list:
            x = my_scale(float(agent.pos[0]), x=True)
            y = my_scale(float(agent.pos[1]), y=True)
            pygame.draw.circle(screen, Color(122, 61, 23), (x, y), 10)

        for p in pokemon_list:
            x = my_scale(float(p.pos[0]), x=True)
            y = my_scale(float(p.pos[1]), y=True)
            if p.type == 1:
                pygame.draw.circle(screen, Color(0, 255, 255), (x, y), 10)
            else:
                pygame.draw.circle(screen, Color(255, 0, 255), (x, y), 10)


        # draw stop button and more attributes for the user comfort
        stop_button = Button(screen, "STOP", FONT, 50, 30, (10, 10), 5)
        stop_button.check_click()
        stop_button.draw()
        time_to_play = FONT.render(f"Time: {float(client.time_to_end()) / 1000}", True, Color(255, 255, 255))
        screen.blit(time_to_play, (320, 10))
        overall_points = FONT.render(f"Points: {str(info.grade)}", True, Color(255, 255, 255))
        screen.blit(overall_points, (520, 10))
        moves_counter = FONT.render(f"Moves: {str(info.moves)}", True, Color(255, 255, 255))
        screen.blit(moves_counter, (720, 10))

        # update screen changes
        display.update()

        # refresh rate
        clock.tick(10)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GUI

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

        if stop_button.pressed:  # check if the client has stopped the game
            client.stop_connection()
            pygame.quit()
            exit(0)

        print(pokemon_list)

# game over