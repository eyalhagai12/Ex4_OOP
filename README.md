# Ex4_OOP

This is our project of "Pokemon game" in Python.

## Description

This is our project of  a "Pokemon game" in which there are 'agents' who travel on a graph where 'pokemons' are scattered everywhere.  
The agents have to collect as many pokemons as they can in cases of 30 and 60 seconds game.  
In this Project we are communicationg with a game server so we send and receive data that is used to update the game in real time.  

## Table of contents

1. [Getting started](#Getting-started)
2. [Technologies](#Technologies)
3. [Game Algorithm](#Main-Algorithm)
4. [Sources](#Sources)

## Getting started

1. Download or clone this repository and find the "`Ex4_Server_v0.0.jar`" file.
2. Open a command line window in the directory of the jar file (the directory of the project)  
3. In the command line type "`Ex4_Server_v0.0.jar {case number}`" and the program will start the server with the wanted game case.  
4. Open another command line window in the same directory  
5. In this command line, type "`python student_code.py`" and the game will begin

## Technologies

* Python 3.9
* Pygame

## Game Algorithm
The main problem was to move the agents in an efficient way across the graph.  
At first, we thought that using the BFS algorithm would be enough, but since the edges of the graph are weighted,  
we have come to the conclusion that using the Dijkstra algortihm for shortest paths would be the better option.  
```
Algorithm:
for pokemon in pokemons:
    agent_id = find_optimal_agent(agents, pokemon, graph)
    pokemon.assigned_agent = agent_id

find_optimal_agent(agents, pokemon, graph):
    minimum_weight = INFINITY
    path = new List
    optimal = none
    for agent in agents:
        if agent is free:
           weight, temppath = graph.shortest_path(agent.src, pokemon.src)
           weight1, temppath1 = graph.shortest_path(pokemon.src, pokemon.dst)
           weight += weight1
           temppath += temppath1
        else: 
           weight, temppath = graph.shortest_path(agent.path[last], pokemon.src)
           weight1, temppath1 = graph.shortest_path(pokemon.src, pokemon.dst)
           weight += weight1
           temppath += temppath1
           
        if weight < min_weight:
           min_weight = weight
           path = temppath
           optimal = agent
    
    optimal.path = path
    return optimal.id
    
shortest_path(graph, source, destination):
    destination.weight, path = dijkstra(graph, source)
    return destination.weight, path
```


## Sources

* **Djikstra's algorithm**: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* **BFS**: https://en.wikipedia.org/wiki/Breadth-first_search  
