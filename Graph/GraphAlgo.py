import json
import threading
from multiprocessing import Process, Manager

import matplotlib.pyplot as plt
import warnings

from Game.Pokemon import Pokemon
from Graph.GraphAlgoInterface import GraphAlgoInterface
from Graph.GraphInterface import GraphInterface
from Graph.DiGraph import DiGraph
from Graph.Edge import Edge
from Graph.Utils import *


def load_poke_from_json(file):
    """
    Loads a graph from a json file.
    @param file: The path to the json file
    @returns True if the loading was successful, False o.w.
    """
    _dict = json.loads(file)

    pokemons = []

    for pokemon in _dict["Pokemons"]:
        pokemon = pokemon["Pokemon"]
        position = float(pokemon["pos"].split(",")[0]), float(pokemon["pos"].split(",")[1])
        value = pokemon["value"]
        typee = pokemon["type"]
        pokemons.append(Pokemon(pos=(float(position[0]), float(position[1])), value=value, type=typee))
    return pokemons


class GraphAlgo(GraphAlgoInterface):
    def __init__(self, g: DiGraph = DiGraph()):
        self.graph = g

    def get_graph(self) -> GraphInterface:
        """
        @returns the directed graph on which the algorithm works on.
        """
        return self.graph

    def save_to_json(self, file):
        """
        Saves the graph in JSON format to a file
        @param file: The path to the out file
        @return: True if the save was successful, False o.w.
        """
        handle_empty_graph(self.graph)
        nodes = [node for node in self.graph.get_all_v().values()]
        edges = [edge for edge in self.graph.edges.values()]
        for i, node in enumerate(nodes):
            temp = {"pos": f"{node.pos[0]},{node.pos[1]},0.0", "id": node.id}
            nodes[i] = temp
        for i, edge in enumerate(edges):
            temp = {"src": edge.src, "w": edge.weight, "dest": edge.dst}
            edges[i] = temp
        j = {"Edges": edges, "Nodes": nodes}
        try:
            with open(file, 'w') as f:
                json.dump(j, fp=f, indent=2)
                return True
        except (Exception,):
            return False

    def load_from_json(self, file):
        """
        Loads a graph from a json file.
        @param file: The path to the json file
        @returns True if the loading was successful, False o.w.
        """
        graph_res = DiGraph()
        _dict = json.loads(file)

        for n in _dict["Nodes"]:
            if "id" in n.keys() and "pos" in n.keys():
                position = n["pos"].split(",")
                idd = n["id"]
                graph_res.add_node(node_id=idd, pos=(float(position[0]), float(position[1])))
            else:
                if "id" in n.keys():
                    idd = n["id"]
                    graph_res.add_node(node_id=idd, pos=None)
                else:
                    graph_res.add_node(node_id=None, pos=None)
        for edge in _dict["Edges"]:
            graph_res.add_edge(edge["src"], edge["dest"], edge["w"])
        self.graph = graph_res
        if self.graph is not None:
            return True
        else:
            return False

    def add_pokemons(self, pokemons: list):
        pass

    def centerPoint(self) -> (int, float):
        """
        Finds the node that has the shortest distance to it's farthest node.
        @returns The nodes id, min-maximum distance
        """
        max_nodes = []
        min_weight = math.inf
        index = -1
        total_nodes = list(self.graph.get_all_v().values())
        length = len(total_nodes)
        if length < 100:
            for node in total_nodes:
                reset_all(self.graph)
                node_id = find_max_distance(self.graph, node)
                temp = self.graph.get_node(node_id)
                max_nodes.append(temp)
                if min_weight > temp.get_weight():
                    min_weight = temp.get_weight()
                    index = node.get_id()

        else:
            max_nodes = Manager().list()
            length = len(total_nodes)

            sub_lists = []
            processes = []
            for i in range(1, 5):
                temp = total_nodes[int(math.floor((i - 1) * (length / 4))): int(math.floor(i * (length / 4)))]
                sub_lists.append(temp)
                process = Process(target=threaded_find_max_distance,
                                  args=(self.graph.__copy__(), temp, max_nodes))
                processes.append(process)
                process.start()
            for process in processes:
                process.join()

            for value in max_nodes:
                if min_weight > value[1]:
                    min_weight = value[1]
                    index = value[0].get_id()

        return index, min_weight

    def shortest_path(self, source: int, destination: int) -> (float, list):
        """
        Returns the shortest path from node id1 to node id2 using Dijkstra's Algorithm
        @param source: The start node id
        @param destination: The end node id
        @return: The distance of the path, a list of the nodes ids that the path goes through
        """
        reset_all(self.graph)
        dijkstra(self.graph, self.graph.get_node(source))
        path = make_shortest_list(self.graph.get_node(destination))
        return self.graph.get_node(destination).get_weight(), path

    def TSP(self, node_lst: list[int]) -> (list[int], float):
        """
        Finds the shortest path that visits all the nodes in the list
        @param node_lst: A list of nodes id's
        @returns A list of the nodes id's in the path, and the overall distance
        """
        return custom_search(self.graph, node_lst)

    def plot_graph(self) -> None:
        """
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed in a random but elegant manner.
        @return: None
          """
        # if graph's node have no position, generate position for them
        handle_empty_graph(self.graph)
        fig = plt.figure()
        axes = fig.add_axes([0, 0, 1, 1])
        nodes = self.graph.get_all_v().values()
        x = [z.pos[0] for z in nodes]
        y = [-z.pos[1] for z in nodes]
        for node in nodes:
            axes.text(node.pos[0], -node.pos[1], node.get_id(),
                      va='top',
                      ha='right',
                      color='black',
                      fontsize=9,
                      bbox=dict(boxstyle='square, pad=0.2', ec='gray', fc='cyan', alpha=0.65),
                      zorder=99
                      )
            for edge in node.get_out_edges().values():
                temp = self.graph.get_node(edge.get_dst())
                axes.annotate("",
                              xy=(node.pos[0], -node.pos[1]),
                              xycoords='data',
                              xytext=(temp.pos[0], -temp.pos[1]),
                              textcoords='data',
                              arrowprops=dict(arrowstyle="->",
                                              connectionstyle="arc3"),
                              )
        plt.scatter(x=x, y=y, color='red')
        plt.show()
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    def __repr__(self):
        return f"{self.graph}"

