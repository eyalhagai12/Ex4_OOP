import math
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
            if pokemon.edge.src in agent.path and pokemon.edge.dst in agent.path:  # need to change this check
                return agent.id

            # find the shortest path from the agent last destination to the pokemon
            print("Eyals path: {}".format(check_agent_path(agent, pokemon, graph)[0]))
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


def check_agent_path(agent, pokemon, algo):
    path = agent.path.copy()
    path.append(pokemon.id)
    new_path, path_weight = algo.TSP(path)
    estimated_path = []

    for idx in new_path:
        if idx not in estimated_path:
            estimated_path.append(idx)

    return estimated_path, path_weight


def current_path_weight(algo: GraphAlgo, agent):
    result = 0

    for i in range(len(agent.path) - 1):
        result += algo.get_graph().get_node(agent.path[i]).get_out_edges()[agent.path[i + 1]].weight

    return result


def best_agent(algo: GraphAlgo, agent_list, pokemon):
    """
    Find best agent for pokemon
    """
    free_agents = [agent for agent in agent_list if len(agent.path) == 0]
    best_agent = None
    best_path = []
    min_path = math.inf

    # if there are free agents find the closest one
    if len(free_agents) > 0:
        for agent in free_agents:
            path_weight, path = algo.shortest_path(agent.src, pokemon.edge.src)
            edge_weight = algo.get_graph().get_edge(pokemon.edge.src, pokemon.id).weight
            total_weight = path_weight + edge_weight

            if total_weight < min_path:
                min_path = total_weight
                best_agent = agent
                best_path = path + [pokemon.edge.dst]
    else:
        # else use tsp to find the ideal path
        for agent in agent_list:
            # current_weight = current_path_weight(algo, agent)
            path, weight = check_agent_path(agent, pokemon, algo)

            if weight < min_path:
                min_path = weight
                best_agent = agent
                best_path = path

    best_agent.path = best_path
    return best_agent
