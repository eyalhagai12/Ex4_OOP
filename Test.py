import math
import os
import time
import unittest
import multiprocessing

from Graph.DiGraph import DiGraph
from Graph.GraphAlgo import GraphAlgo
from client import Client


def open_server():
    os.system('java -jar Ex4_Server_v0.0.jar 0')


class GraphAlgoTestCase(unittest.TestCase):

    def test_load_from_json(self):
        process = multiprocessing.Process(target=open_server)
        start = time.time()
        process.start()
        while time.time() - start < 1:
            continue
        try:
            PORT = 6666
            HOST = '127.0.0.1'

            client = Client()
            client.start_connection(HOST, PORT)
            graph_algo = GraphAlgo(DiGraph())
            graph_algo.load_from_json(client.get_graph())
            self.assertNotEqual(graph_algo.graph.__repr__(), "Graph: |V|=0 , |E|=0")
            print(graph_algo.graph)
            client.stop_connection()
            os.system('exit')
        except ResourceWarning as e:
            print("Test is finished")

    def test_shortest_path(self):
        process = multiprocessing.Process(target=open_server)
        start = time.time()
        process.start()
        while time.time() - start < 1:
            continue
        try:
            PORT = 6666
            HOST = '127.0.0.1'

            client = Client()
            client.start_connection(HOST, PORT)
            graph_algo = GraphAlgo(DiGraph())
            graph_algo.load_from_json(client.get_graph())
            tup = graph_algo.shortest_path(3, 9)
            self.assertNotEqual(tup[0], 0)
            self.assertNotEqual(tup[0], math.inf)
            print(tup[1])
            client.stop_connection()
            os.system('exit')
        except ResourceWarning as e:
            print("Test is finished")

    def test_centerPoint(self):
        process = multiprocessing.Process(target=open_server)
        start = time.time()
        process.start()
        while time.time() - start < 2:
            continue
        try:
            PORT = 6666
            HOST = '127.0.0.1'

            client = Client()
            client.start_connection(HOST, PORT)
            graph_algo = GraphAlgo(DiGraph())
            graph_algo.load_from_json(client.get_graph())
            tup = graph_algo.centerPoint()
            self.assertNotEqual(tup[0], None)
            self.assertNotEqual(tup[0], math.inf)
            print(tup[0], ', ', tup[1])
            client.stop_connection()
            os.system('exit')
        except ResourceWarning as e:
            print("Test is finished")


if __name__ == '__main__':
    unittest.main()
