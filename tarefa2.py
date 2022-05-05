from posixpath import split
from typing import get_args
from tarefa2.agents import AgentS
from tarefa2.agentl import AgentL

def get_ambiente(filename):
    ambiente = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.split()
            ambiente[line[0]] = []
            for coord in line[1:]:
                coord = coord.split(",")
                x = int(coord[0])
                y = int(coord[1])
                ambiente[line[0]].append((x,y))
    return ambiente

def get_config(filename):
    config = {}
    with open(filename, "r") as f:
        for line in f:
            line = line.split('=')
            config[line[0]] = int(line[1])
    return config

def get_difacesso(filename):
    difacesso = []
    with open(filename, "r") as f:
        for line in f:
            line = line.split()
            line = list(map(float, line))
            difacesso.append(line)
    return difacesso

def get_vitals(filename):
    sinaisvitais = []
    with open(filename, "r") as f:
        for line in f:
            line = line.split()
            line = list(map(float, line))
            sinaisvitais.append(line)
    return sinaisvitais

def print_maze(maze, victims):
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if (i, j) in victims and maze[i][j]:
                print("V", end="")
            elif maze[i][j]:
                print(" ", end="")
            else:
                print("#", end="")
        print()
    print()

def main(args):
    ambiente = get_ambiente("config_data/ambiente.txt")
    config = get_config("config_data/config.txt")
    costs = get_difacesso("config_data/difacesso.txt")
    vitals = get_vitals("config_data/sinaisvitais.txt")

    origin = ambiente['Agente'][0]
    victims = ambiente['Vitima']
    walls = ambiente['Parede']
    agent = AgentL(origin, victims, walls, config)
    agent.make_maze()
    maze = agent.get_maze()

    print_maze(maze, victims)
    
    origin = ambiente['Agente'][0]
    victims = ambiente['Vitima']

    agent = AgentS(origin, victims, vitals, costs, config)
    agent.random_individuals(100)
    agent.run_gens(args.generations, log=True)
    agent.print_performance()

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Tarefa 2')
    parser.add_argument('-n', '-g', '--generations', type=int,
                        help='Gerações a serem executadas', default=200)
    args = parser.parse_args()
    return args

args = get_args()
main(args)