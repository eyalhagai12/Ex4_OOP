import math as mt

from Game.Agent import Agent
from Game.Pokemon import Pokemon
from Graph.GraphAlgo import GraphAlgo
from client import Client


def run_agent(agent: Agent, g_algo: GraphAlgo, client: Client, stop: bool):
    while len(agent.path) != 0:
        p = agent.path[0]
        if stop:  # global bool variable indicate when one pokemon found
            return
        client.choose_next_edge(
            '{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(agent.path[1 % len(agent.path)]) + '}')
        agent.pos = g_algo.get_graph().nodes[agent.path[1 % len(agent.path)]].pos
        agent.path.remove(agent.path[0])


def find_optimal_agent(agent_list: list, pokemon: Pokemon, graph: GraphAlgo) -> int:
    free = []
    min_weight = mt.inf
    path = []
    optimal = None

    # find free agents
    for agent in agent_list:
        if len(agent.path) == 0:
            free.append(agent)

    if len(free) != 0:  # in case there are free agents
        for agent in free:  # loop on the free list
            weight, temppath = graph.shortest_path(agent.src,
                                                   pokemon.edge.src)  # find the shortest path from agent to pokemon
            weight1, temppath1 = graph.shortest_path(pokemon.edge.src, pokemon.edge.dst)
            weight += weight1
            temppath += temppath1
            # in case we found an agent with shorter path, set this agent as optimal
            if weight < min_weight:
                min_weight = weight
                path = temppath
                optimal = agent

        optimal.path = path  # update optimal path
        print(optimal.path)
        return optimal.id

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
            # in case we found an agent with a shorter path, set this agent as optimal
            if weight < min_weight:
                min_weight = weight
                path = temppath
                optimal = agent

        optimal.path += path  # update optimal path
        print(optimal.path)
        return optimal.id
