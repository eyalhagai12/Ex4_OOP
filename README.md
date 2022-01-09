# Ex4_OOP

This is our project of "Pokemon game" in Python.  
![simplescreenrecorder-2022-01-08_15 41 10](https://user-images.githubusercontent.com/77681248/148648287-16850383-06ce-4178-a563-34c4aaad0e48.gif)



## Description

This is our project of  a "Pokemon game" in which there are 'agents' who travel across a graph where 'pokemons' are scattered everywhere.  
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
the algorithm we chose is very simple and yields good results. first we initialize each agent in the node that is the center of the graph. 
then, in each iteration we look at each agents position and send it to the closest pokemon to him (this is done using shortest path with djikstra).
we make sure that each pokemon is always targeted only by one agent, and we only do the calculation for an agent when the agent is not moving.

for each agent we iterate over all the pokemons and pick the closest one and then we assign this agent to that pokemon, thus blocking others
from trying to reach the same pokemon and waste time.

#### Code in student_code.py:
```
 for agent in agents:
            if agent.dest == -1:
                pokemon = Utils.closest_pokemon(copy_algo, agent, pokemon_list)
                Utils.move_agent(copy_algo, agent, client)
  
```

#### Code in Utils.py:
```
 closest_pokemon(algo: GraphAlgo, agent, pokemon_list: list):
    """
    Find the closest pokemon to a given agent
    """
    pokemon_list.sort(key=lambda x: x.value, reverse=True)
    min_weight = math.inf
    c_pokemon = None
    best_path = []

    # loop over all pokemons and find the closest
    for pokemon in pokemon_list:
        if pokemon.assigned_agent == -1 or pokemon.assigned_agent == agent.id:
            weight, path = algo.shortest_path(agent.src, pokemon.edge.src)
            edge_weight = pokemon.edge.weight
            path.append(algo.graph.get_node(pokemon.edge.dst).id)

            total_weight = (weight + edge_weight) / pokemon.value

            if total_weight < min_weight:
                c_pokemon = pokemon
                min_weight = total_weight
                best_path = path

    if c_pokemon:
        best_path.pop(0)
        c_pokemon.assigned_agent = agent.id
        agent.path = best_path

    return c_pokemon
```

## Sources

* **Djikstra's algorithm**: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* **BFS**: https://en.wikipedia.org/wiki/Breadth-first_search  
