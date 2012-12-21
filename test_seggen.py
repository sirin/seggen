#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import rndPair, BitGene
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from test.utility import Utility
from random import choice
import random
import math

test_list = [1,0,1,0,0,0,0,1,0,0]

#return a pair which has greatest key
def choose_best(dict):
    return sorted(dict.iteritems(),reverse=True)[0]

class Flow:

    def choose_pareto(self, population):
        temp = []
        pareto_set = []
        for j in population:
            temp.append(j.list_repr())
        pareto_set = TestOrganismPopulation.utility.non_dominated(temp)
        return pareto_set

    def create_pareto_fitness_dict(self, population, pareto_set, pareto_formal):
        pareto_hardness_dict = {}
        for pareto_ind, key in zip(pareto_set,pareto_formal):
            count = 0.0
            for ind in population.list_repr():
                if TestOrganismPopulation.utility.dominates(pareto_ind, ind):
                    count += 1
            pareto = count / (len(population)+1)
            pareto_hardness_dict[key] = pareto
        return pareto_hardness_dict

    def create_population_fitness_dict(self, population, pareto_set, pareto_formal):
        population_fitness_dict = {}
        par_fit_list = self.create_pareto_fitness_dict(population, pareto_set, pareto_formal).values()
        for ind, ind_real in zip(population.list_repr(), population):
            sum_fit = 1.0
            for pareto_ind, fit in zip(pareto_set, par_fit_list):
                if TestOrganismPopulation.utility.dominates(pareto_ind, ind):
                    sum_fit += fit
            population_fitness_dict[ind_real] = 1.0/sum_fit
        return population_fitness_dict

    def roulette_wheel_pop(self, population, pareto_set, formal_pareto,num):
        fitnesses = []
        fitnesses = self.create_population_fitness_dict(population, pareto_set, formal_pareto).values()
        total_fit = float(sum(fitnesses))
        rel_fitness = [f/total_fit for f in fitnesses]
        probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
        new_population = []
        for n in xrange(num):
            r = random.random()
            for (i, individual) in enumerate(population):
                if r <= probs[i]:
                    new_population.append(individual)
                    break
        return new_population

    def roulette_wheel_pareto(self, population, pareto_set, formal_pareto, num):
        fitnesses = []
        fitnesses = self.create_pareto_fitness_dict(population,pareto_set, formal_pareto).values()
        total_fit = float(sum(fitnesses))
        rel_fitness = [f/total_fit for f in fitnesses]
        probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
        new_population = []
        for n in xrange(num):
            r = random.random()
            for (i, individual) in enumerate(formal_pareto):
                if r <= probs[i]:
                    new_population.append(individual)
                    break
        return new_population

class TestGene(BitGene):

    mutProb = 0.1
    mutAmt = 10.0

    randMin = 0x0
    randMax = 0xff

    def __add__(self, other):
        return (self.value + other.value) / 2

# generate a genome, one gene for each binary in the list
genome = {}
for i in range(len(test_list)):
    genome[str(i)] = TestGene


class TestOrganism(Organism):
    genome = genome
    Pmc = 0.8

    def __len__(self):
        return len(self.genome)

    def __repr__(self):
        """
        Return the gene values as a string
        """
        bits = []
        for k in xrange(self.numgenes):
            n = self.genes[str(k)].value
            bits.append(n)
        return repr(bits)

    def list_repr(self):
        """
        Return the gene values as a list
        """
        bits = []
        for k in xrange(self.numgenes):
            n = self.genes[str(k)].value
            bits.append(n)
        return bits

    def fitness(self):
        """
        calculate fitness, as the absolute value of the
        subtract of each bit gene from the
        corresponding bit of the target list
        """
        diffs = 0
        #for i in xrange(self.numgenes):
            #x0 = test_list[i]
            #x1 = self[i]
            #diffs += abs(x0 - x1)
        return diffs

    def crossover(self, other):
        p = random.randint(0,self.__len__()-1)
        offspring1 = self.list_repr()[:p] + other.list_repr()[p:]
        offspring2 = other.list_repr()[:p] + self.list_repr()[p:]
        return offspring1, offspring2

    def mutation_pms(self, other, pms):
        p = random.uniform(0,1)
        if p <= pms:
            self = other
        return self

    #with a probability Pmc that shifts a boundary of the individual to the next sentence.
    def mutation_pmc(self):
        p = random.uniform(0,1)
        r = random.randint(0,self.__len__()-2)
        if p <= self.Pmc:
            self.genes[str(r)].value, self.genes[str(r+1)].value = self.genes[str(r+1)].value, self.genes[str(r)].value
        return self

class TestOrganismPopulation(Population):

    utility = Utility()
    initPopulation = 10
    species = TestOrganism
    # cull to this many children after each generation
    childCull = 10

    # number of children to create after each generation
    childCount = 40

    def override_best(self, list):
        list.sort()
        return list[0]

    def list_repr(self):
        temp = []
        for j in self:
            temp.append(j.list_repr())
        return temp

    def pareto_formal(self, pareto_set):
        formal = []
        for i in pareto_set:
            for j, k in zip(self.list_repr(), self):
                if i == j:
                    formal.append(k)
        return formal

    def pareto_list_to_str(self, par_list):
        pareto_set_official =[]
        for x in par_list:
            pareto_set_official.append(' '.join(str(elem) for elem in x))
        return pareto_set_official

# start with a population of 10 random organisms
ph = TestOrganismPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    flow = Flow()
    while i < 1:
        pareto = flow.choose_pareto(ph)
        formal_pareto = ph.pareto_formal(pareto)
        pareto_fit_dict = flow.create_pareto_fitness_dict(ph, pareto, formal_pareto)
        print "pareto"
        print pareto_fit_dict

        pop_fit_dict = flow.create_population_fitness_dict(ph, pareto, formal_pareto)
        print "pop"
        print pop_fit_dict

        pareto_size = random.randint(1,len(pareto)-1)
        pop_size = (ph.__len__()-pareto_size)

        select_from_pop = flow.roulette_wheel_pop(ph, pareto, formal_pareto, pop_size)
        select_from_pareto = flow.roulette_wheel_pareto(ph, pareto, formal_pareto, pareto_size)
        mating_pool = select_from_pop+select_from_pareto
        print "mating pool"
        print mating_pool

        children = []
        for i in range(0,5):
            indexes = random.sample(set(range(len(mating_pool))), 2)
            children += mating_pool[indexes[0]].crossover(mating_pool[indexes[1]])
        print "children (after crossover)"
        print children

        r = random.randint(0,len(children)-1)
        children[indexes[0]] = children[indexes[0]].mutation_pms(children[r],0.4)
        print "after mutation pms"
        print children
        print children[indexes[0]]
        mutated_pmc = children[indexes[0]].mutation_pmc()
        print "after mutation pmc"
        print mutated_pmc
        children.append(mutated_pmc)
        print "after mutation pmc"
        print children

        #b = ph.best()
        #if b.fitness() == 0:
            #print "cracked!"
            #break
        i += 1
        #mating_pool.gen()
        #ph.gen()

if __name__ == '__main__':
    main()