from pkg.block import Block
import random 
from math import floor 

class AgentS(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, origin, victims, vitals, difficult, config):
        x,y = origin
        super().__init__(x, y, "agents")
        self.base_x = x
        self.base_y = y
        self.origin = origin

        self.rows = config['maxLin']
        self.columns = config['maxCol']

        self.victims = victims
        self.vitals = self.map_vitals(vitals)
        self.access_time = self.map_access_time(difficult)

        self.Ts = config['Ts']
        self.Ks = config['Ks']

        self.directions = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']
        self.direction_cost = {
            'N': 1, 'S': 1, 'E': 1, 'W': 1, 
            'NE': 1.5, 'NW': 1.5, 'SE': 1.5, 'SW': 1.5}

        self.individuals = []

        self.generation = 0
        
        self.pCROSS = 0.8
        self.pMUT = 0.05


    def map_vitals(self, vitals):
        new_vitals = {}
        for i in range(len(vitals)):
            new_vitals[self.victims[i]] = vitals[i][-1]
        return new_vitals 
    
    def map_access_time(self, difficult):
        new_access_time = {}
        for i in range(len(difficult)):
            new_access_time[self.victims[i]] = difficult[i][-1]
        return new_access_time

    def print_victims(self):
        print("Vitals:")

        print(f"Victim\tVital\tDifficult")
        for i in range(len(self.victims)):
            print(f"{self.victims[i]} \t {self.vitals[self.victims[i]]} \t {self.difficult[self.victims[i]]}")
        print()

    def calc_fitness(self, individual):
        saved = 0
        severities = 0
        time = 0
        
        for i in range(len(individual)):
            saved+=individual[i]
            if individual[i] == 1:
                severities+=self.vitals[self.victims[i]]
                time+=self.access_time[self.victims[i]]
                
        if time>self.Ts: return 1    
        fitness = 1+severities*1000+(1-float(time)/self.Ts)
        return fitness

    def calc_all_fitness(self, individuals):
        fitness = []
        for individual in individuals:
            fitness.append(self.calc_fitness(individual))
        return fitness

    def normalization(self, values):
        sum_values = sum(values)
        normalized = []
        for value in values:
            normalized.append(value/sum_values)
        return normalized

    def russian_roulette(self, individuals, fit_norm, R):
        descendents = []
        while len(descendents) < R:
            i=0
            p_sum = fit_norm[i]
            r = random.random() # [0.0,1.0)
            while p_sum < r:
                i=i+1
                p_sum+=fit_norm[i]
            descendents.append(individuals[i])
        
        return descendents
    
    def crossover(self, ind1, ind2, pCROSS):
        div = int(len(ind1)*pCROSS)
        son1 = ind1[:div] + ind2[div:]
        son2 = ind2[:div] + ind1[div:]
        return son1, son2

    def recombine(self, individuals, pCROSS):
        new_individuals = individuals
        for i in range(len(individuals)):
            for j in range(i+1, len(individuals)):
                son1, son2 = self.crossover(individuals[i], individuals[j], pCROSS)
                new_individuals.append(son1)
                new_individuals.append(son2)
        return new_individuals

    def mutate(self, individuals, pMUT):
        for individual in individuals:
            for i in range(len(individual)):
                if random.random() < pMUT:
                    individual[i] = 1-individual[i]
        return individuals
    
    def best_individuals(self, individuals, fitness, N):
        individuals = [''.join(map(str,ind)) for ind in individuals]
        fit = {}
        
        for i in range(len(individuals)):
            fit[individuals[i]]= fitness[i]

        individuals.sort(key=fit.get, reverse=True)

        fitness = [fit[individual] for individual in individuals]

        individuals = [list(map(int, list(ind))) for ind in individuals]

        return individuals[:N], fitness[:N]

    def get_best_individual(self, individuals=None, fitness=None):
        if individuals is None: individuals = self.individuals
        if fitness is None: fitness = self.fitness
        best = 0
        for i in range(len(individuals)):
            if fitness[i] > fitness[best]:
                best = i
        return best

    def genetic_algorithm_generation(self, N, R, pCROSS, pMUT):
        if R>len(self.individuals): return
        fit_norm = self.normalization(self.fitness)
        descendents = self.russian_roulette(self.individuals, fit_norm, R)
        # print("Descendents:")
        # self.print_individuals(descendents)
        descendents = self.recombine(descendents, pCROSS)
        descendents = self.mutate(descendents, pMUT)

        fitness = self.calc_all_fitness(descendents)
        self.individuals, self.fitness = self.best_individuals(descendents, fitness, N)
    
        self.generation+=1
        pass

    def random_individual(self):
        individual = []
        alleles = [0,1]
        for victim in self.victims:
            individual.append(random.randint(0,1))
        return individual

    def random_individuals(self, N):
        self.individuals = []
        for _ in range(N):
            individual = self.random_individual()
            self.individuals.append(individual)
        self.fitness = self.calc_all_fitness(self.individuals)
        self.generation = 0
    
    def print_individual(self, individual):
        gen = str(self.generation)
        ind = ''.join(map(str,individual))
        fit = str(int(self.calc_fitness(individual)))
        tim = 0
        ser = 0
        for i, val in enumerate(individual):
            if val == 1:
                tim+=self.access_time[self.victims[i]]
                ser+=self.vitals[self.victims[i]]
        tim = str(int(tim))
        ser = str(float(ser))

        print("{:>12}{:>50}{:>13}{:>13.4}{:>13}".format(gen, ind, tim, ser, fit))
        
    def print_headers(self):
        print("{:>12}{:>50}{:>13}{:>13}{:>13}".format("Generation", "Individual", "Ts", "Severity", "Fitness"))

    def print_best(self):
        best = self.get_best_individual(self.individuals, self.fitness)
        self.print_individual(self.individuals[best])

    def print_first(self):
        self.print_headers()
        self.print_best()

    def print_individuals(self, individuals=None):
        if individuals is None: individuals = self.individuals
        self.print_headers()

        for individual in individuals:
            self.print_individual(individual)

    def run_gens(self, gens, N=5, R=5, pCROSS=0.8, pMUT=0.05, log=False):
        if log: self.print_first()
        while gens>0:
            self.genetic_algorithm_generation(N, R, pCROSS, pMUT)
            if log: self.print_best()
            gens-=1

        if log: print()
    
    def print_performance(self):
        vs = 0  # Total de vítimas salvas
        ts = 0  # Tempo gasto
        G = 0  # Gravidade acumulada
        
        Se = 0
        St = 0
        
        best = self.get_best_individual()
        tot_victims = len(self.individuals[best])
        for i in range(tot_victims):
            if self.individuals[best][i]:
                vs+=1
                ts+=self.access_time[self.victims[i]]
                G+=self.vitals[self.victims[i]]
                Se+=floor(self.vitals[self.victims[i]]*5) 
            St+=floor(self.vitals[self.victims[i]]*5) 
        
        S = vs/ts 
        Se = Se/(ts*St)

        print(f"V_s: {vs}")
        print(f"t_s: {ts}")
        print(f"T: {tot_victims}")
        print(f"G: {G}")
        print(f"S: {S}")
        print(f"S_e: {Se}")

