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
    parents = []
    children = []

    def get_children(self):
        return self.children

    def get_parents(self):
        return self.parents

    def clear_children(self):
        del self.children[:]

    def clear_parents(self):
        del self.parents[:]

    #return list
    def choose_pareto(self, my_list):
        temp = []
        pareto_set = []
        pareto_set = TestOrganismPopulation.utility.non_dominated(my_list)
        return pareto_set

    #return dict {str(list):float}
    def create_pareto_fitness_dict(self, population, pareto_set):
        pareto_hardness_dict = {}
        for pareto_ind in pareto_set:
            count = 0.0
            if type(population) != list:
                population = population.list_repr()
            for ind in population:
                if TestOrganismPopulation.utility.dominates(pareto_ind, ind):
                    count += 1
            pareto = count / (len(population)+1)
            pareto_hardness_dict[str(pareto_ind)] = pareto
        return pareto_hardness_dict

    #return dict {str(list):float}
    def create_population_fitness_dict(self, population, pareto_set):
        population_fitness_dict = {}
        par_fit_list = self.create_pareto_fitness_dict(population, pareto_set).values()
        if type(population) != list:
            population = population.list_repr()
        for ind in population:
            sum_fit = 1.0
            for pareto_ind, fit in zip(pareto_set, par_fit_list):
                if TestOrganismPopulation.utility.dominates(pareto_ind, ind):
                    sum_fit += fit
            population_fitness_dict[str(ind)] = 1.0/sum_fit
        return population_fitness_dict

    #return list
    def roulette_wheel_pop(self, population, pareto_set, num):
        fitnesses = self.create_population_fitness_dict(population, pareto_set).values()
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

    #return list
    def roulette_wheel_pareto(self, population, pareto_set, num):
        fitnesses = self.create_pareto_fitness_dict(population,pareto_set).values()
        total_fit = float(sum(fitnesses))
        rel_fitness = [f/total_fit for f in fitnesses]
        probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
        new_population = []
        for n in xrange(num):
            r = random.random()
            for (i, individual) in enumerate(pareto_set):
                if r <= probs[i]:
                    new_population.append(individual)
                    break
        return new_population

    #return two lists
    def crossover(self, organism1, organism2):
        p = random.randint(0, len(organism1)-1)
        offspring1 = organism1[:p] + organism2[p:]
        offspring2 = organism2[:p] + organism1[p:]
        return offspring1, offspring2

    #return list
    def mutation_pms(self, organism1, organism2, pms):
        p = random.uniform(0,1)
        if p <= pms:
            organism1 = organism2
        return organism1

    #with a probability Pmc that shifts a boundary of the individual to the next sentence.
    #return list
    def mutation_pmc(self, organism):
        p = random.uniform(0,1)
        r = random.randint(0,len(organism)-2)
        if p <= TestOrganism.Pmc:
            organism[r], organism[r+1] = organism[r+1], organism[r]
        return organism

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

    def len(self):
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

# start with a population of 10 random organisms
ph = TestOrganismPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    flow = Flow()
    while i < 10:
        if i == 0:
            for ind in ph:
                flow.parents.append(ind.list_repr())
            pareto = flow.choose_pareto(flow.get_parents())
        elif i > 0:
            new_pareto = flow.choose_pareto(flow.get_children())
            pareto = pareto+new_pareto
            pareto = TestOrganismPopulation.utility.non_dominated(pareto)
            flow.clear_parents()
            for par in flow.get_children():
                flow.parents.append(par)
            flow.clear_children()

        pareto_size = random.randint(1,len(pareto))
        pop_size = (len(flow.get_parents())-pareto_size)

        #ga operator: selection
        select_from_pop = flow.roulette_wheel_pop(flow.get_parents(), pareto, pop_size)
        select_from_pareto = flow.roulette_wheel_pareto(flow.get_parents(), pareto, pareto_size)
        mating_pool = select_from_pop+select_from_pareto

        #ga operator: crossover
        for j in range(0,5):
            indexes = random.sample(set(range(len(mating_pool))), 2)
            flow.children += flow.crossover(mating_pool[indexes[0]], mating_pool[indexes[1]])

        #ga operator: mutation
        rand_indexes = random.sample(set(range(len(flow.children))), 2)
        flow.children[rand_indexes[0]] = flow.mutation_pms(flow.children[rand_indexes[0]], flow.children[rand_indexes[1]], 0.4)
        mutated_pmc = flow.mutation_pmc(flow.children[rand_indexes[0]])
        flow.children.append(mutated_pmc)
        print "%d. step pareto archive" % (i+1)
        for p in pareto:
            print p

        i += 1

if __name__ == '__main__':
    main()