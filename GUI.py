
from client import Client
from pygame import gfxdraw
import pygame
from pygame import *
from Game.GameInfo import GameInfo
from Graph.GraphAlgo import GraphAlgo
from Graph.Button import Button


class GUI:
    def __init__(self, graph_algo: GraphAlgo, agents: list, pokemons: list, client: Client):
        self.graph_algo = graph_algo
        self.agents = agents
        self.pokemons = pokemons
        self.info = None
        self.client = client

        # init pygame
        width, height = 1080, 720
        pygame.init()
        pygame.font.init()

        self.screen = display.set_mode((width, height), depth=32, flags=RESIZABLE)
        self.screen.fill(Color(0, 0, 0))
        self.clock = pygame.time.Clock()

        self.FONT = pygame.font.SysFont('Arial', 20, bold=True)

        # get data proportions
        self.min_x = min(list(graph_algo.graph.nodes.values()), key=lambda n: n.pos[0]).pos[0]
        self.min_y = min(list(graph_algo.graph.nodes.values()), key=lambda n: n.pos[1]).pos[1]
        self.max_x = max(list(graph_algo.graph.nodes.values()), key=lambda n: n.pos[0]).pos[0]
        self.max_y = max(list(graph_algo.graph.nodes.values()), key=lambda n: n.pos[1]).pos[1]

        self.radius = 15

        # GUI annotations
        self.stop_button = None
        self.play_time = None
        self.points = None
        self.num_of_moves = None

    def set_info(self, info: GameInfo):
        self.info = info

    def set_agents(self, agents: list):
        self.agents = agents

    def set_pokemons(self, pokemons: list):
        self.pokemons = pokemons

    def scale(self, data, min_screen, max_screen, min_data, max_data):
        """
        get the scaled data with proportions min_data, max_data
        relative to min and max screen dimentions
        """
        return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen

    # decorate scale with the correct values
    def my_scale(self, data, x=False, y=False):
        if x:
            return self.scale(data, 50, self.screen.get_width() - 50, self.min_x, self.max_x)
        if y:
            return self.scale(data, 50, self.screen.get_height() - 50, self.min_y, self.max_y)

    def draw_nodes(self):
        for n in self.graph_algo.graph.nodes.values():
            x = self.my_scale(n.pos[0], x=True)
            y = self.my_scale(n.pos[1], y=True)
            # its just to get a nice antialiased circle
            gfxdraw.filled_circle(self.screen, int(x), int(y),
                                  self.radius, Color(64, 80, 174))
            gfxdraw.aacircle(self.screen, int(x), int(y),
                             self.radius, Color(255, 255, 255))

            # draw the node id
            id_srf = self.FONT.render(str(n.id), True, Color(0, 0, 0))
            rect = id_srf.get_rect(center=(x, y))
            self.screen.blit(id_srf, rect)

    def draw_edges(self):
        # draw edges
        for e in self.graph_algo.graph.edges.values():
            # find the edge nodes
            src = next(n for n in self.graph_algo.graph.nodes.values() if n.id == e.src)
            dest = next(n for n in self.graph_algo.graph.nodes.values() if n.id == e.dst)

            # scaled positions
            src_x = self.my_scale(src.pos[0], x=True)
            src_y = self.my_scale(src.pos[1], y=True)
            dest_x = self.my_scale(dest.pos[0], x=True)
            dest_y = self.my_scale(dest.pos[1], y=True)

            # draw the line
            pygame.draw.line(self.screen, Color(61, 72, 126),
                             (src_x, src_y), (dest_x, dest_y))

    def draw_agents(self):
        # draw agents
        for agent in self.agents:
            x = self.my_scale(float(agent.pos[0]), x=True)
            y = self.my_scale(float(agent.pos[1]), y=True)
            pygame.draw.circle(self.screen, Color(122, 61, 23), (x, y), 10)

    def draw_pokemons(self):
        # draw pokemons
        for p in self.pokemons:
            x = self.my_scale(float(p.pos[0]), x=True)
            y = self.my_scale(float(p.pos[1]), y=True)
            if p.type == 1:
                pygame.draw.circle(self.screen, Color(0, 255, 255), (x, y), 10)
            else:
                pygame.draw.circle(self.screen, Color(255, 0, 255), (x, y), 10)

    def draw_button(self, func):
        # draw stop button and more attributes for the user comfort
        if self.stop_button is None:
            self.stop_button = Button(self.screen, "STOP", self.FONT, 50, 30, (10, 10), 5, func)
        self.stop_button.check_click()
        self.stop_button.draw()

    def draw_info(self):
        self.play_time = self.FONT.render(f"Time: {float(self.client.time_to_end()) / 1000}", True,
                                          Color(255, 255, 255))
        self.screen.blit(self.play_time, (320, 10))
        self.points = self.FONT.render(f"Points: {str(self.info.grade)}", True, Color(255, 255, 255))
        self.screen.blit(self.points, (520, 10))
        self.num_of_moves = self.FONT.render(f"Moves: {str(self.info.moves)}", True, Color(255, 255, 255))
        self.screen.blit(self.num_of_moves, (720, 10))

    def run_gui(self, info: GameInfo, func):
        # check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

        # refresh surface
        self.screen.fill(Color(0, 0, 0))

        self.set_info(info)

        # draw elements
        self.draw_edges()
        self.draw_nodes()
        self.draw_agents()
        self.draw_pokemons()
        self.draw_button(func)
        self.draw_info()

        # update screen changes
        display.update()
        # refresh rate
        # self.clock.tick(10)
