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

def find_optimal_agent(g_algo: GraphAlgo, pokemon: Pokemon, agent_list: list):
    free = []
    for agent in agent_list:
        if agent.path is None:
            free.append(agent)

    min_weight = math.inf
    path = []
    optimal = None
    # if there are free agents, find the shortest path from each agent's source to the pokemon
    if free:
        for agent in free:
            w, p = g_algo.shortest_path(agent.src, pokemon.id)
            if min_weight > w:
                min_weight = w
                path = p
                optimal = agent
        optimal._path = path
        return optimal.id
    # return the optimal agent's id that has the optimal path to the pokemon
    # if no agents are free, find the optimal agent and concat the additional path to its original path
    else:
        for agent in agent_list:
            # if the pokemon is already in the agent's path, this is the optimal agent
            if pokemon.id in agent.path:
                return agent.id
            w, p = g_algo.shortest_path(agent.path[-1], pokemon.id)
            if min_weight > w:
                min_weight = w
                path = p
                optimal = agent
        optimal.path.extend(path)
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

    pokemons = client.get_pokemons()
    pokemons_obj = json.loads(pokemons, object_hook=lambda d: SimpleNamespace(**d))

    print(pokemons)

    graph_json = client.get_graph()

    FONT = pygame.font.SysFont('Arial', 20, bold=True)
    # load the json string into SimpleNamespace Object

    graph = json.loads(
        graph_json, object_hook=lambda json_dict: SimpleNamespace(**json_dict))

    for n in graph.Nodes:
        x, y, _ = n.pos.split(',')
        n.pos = SimpleNamespace(x=float(x), y=float(y))

    # get data proportions
    min_x = min(list(graph.Nodes), key=lambda n: n.pos.x).pos.x
    min_y = min(list(graph.Nodes), key=lambda n: n.pos.y).pos.y
    max_x = max(list(graph.Nodes), key=lambda n: n.pos.x).pos.x
    max_y = max(list(graph.Nodes), key=lambda n: n.pos.y).pos.y

    radius = 15
    # create info object and add agents
    info = load_info_from_json(client.get_info())
    for i in range(info.agents):
        client.add_agent("{\"id\":" + str(i) + "}")

    # this commnad starts the server - the game is running now
    client.start()

    while client.is_running() == 'true':
        # get info from server
        info = load_info_from_json(client.get_info())
        # initialize pokemon list
        pokemon_list = load_pokemons_from_json(client.get_pokemons())
        agent_list = load_agents_from_json(client.get_agents())
        
        # build graph copy for algorithms
        graph_cpy = graph_algo.graph.__copy__()
        for pokemon in pokemon_list:
            idd = max(graph_cpy.get_all_v().keys()) + 1
            graph_cpy.add_node(node_id=idd, pos=pokemon.pos, value=pokemon.value, type=pokemon.type)
            tup = graph_algo.graph.find_edge_for_pokemon(pokemon)
            graph_cpy.add_edge(tup[0].src, idd, tup[1])
            graph_cpy.add_edge(idd, tup[0].dst, tup[2])
            pokemon.edge = tup[0]
            graph_cpy.remove_edge(tup[0].src, tup[0].dst)

        # check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

        # refresh surface
        screen.fill(Color(0, 0, 0))

        # draw nodes
        for n in graph.Nodes:
            x = my_scale(n.pos.x, x=True)
            y = my_scale(n.pos.y, y=True)

            # its just to get a nice antialiased circle
            gfxdraw.filled_circle(screen, int(x), int(y),
                                radius, Color(64, 80, 174))
            gfxdraw.aacircle(screen, int(x), int(y),
                            radius, Color(255, 255, 255))

            # draw the node id
            id_srf = FONT.render(str(n.id), True, Color(255, 255, 255))
            rect = id_srf.get_rect(center=(x, y))
            screen.blit(id_srf, rect)

        # draw edges
        for e in graph.Edges:
            # find the edge nodes
            src = next(n for n in graph.Nodes if n.id == e.src)
            dest = next(n for n in graph.Nodes if n.id == e.dest)

            # scaled positions
            src_x = my_scale(src.pos.x, x=True)
            src_y = my_scale(src.pos.y, y=True)
            dest_x = my_scale(dest.pos.x, x=True)
            dest_y = my_scale(dest.pos.y, y=True)

            # draw the line
            pygame.draw.line(screen, Color(61, 72, 126),
                            (src_x, src_y), (dest_x, dest_y))

        # draw agents
        for agent in agents:
            pygame.draw.circle(screen, Color(122, 61, 23),
                            (int(agent.pos.x), int(agent.pos.y)), 10)
        # draw pokemons (note: should differ (GUI wise) between the up and the down pokemons (currently they are marked in the same way).
        for p in pokemons:
            pygame.draw.circle(screen, Color(0, 255, 255), (int(p.pos.x), int(p.pos.y)), 10)

        # update screen changes
        display.update()

        # refresh rate
        clock.tick(10)

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

        

        client.move()
    # game over:


