#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import rndPair, BitGene
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from test.utility import Utility
from random import choice
import random
import math

test_list = [1,0,1]

#return a pair which has greatest key
def choose_best(dict):
    return sorted(dict.iteritems(),reverse=True)[0]

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
            other = self
        return other

class TestOrganismPopulation(Population):

    utility = Utility()
    initPopulation = 5
    species = TestOrganism
    # cull to this many children after each generation
    childCull = 5

    # number of children to create after each generation
    childCount = 40

    def override_best(self, list):
        list.sort()
        return list[0]

    def roulette_wheel_pop(self, pareto_set, num):
        fitnesses = []
        fitnesses = self.create_population_fitness_dict(pareto_set).keys()
        total_fit = float(sum(fitnesses))
        rel_fitness = [f/total_fit for f in fitnesses]
        probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
        new_population = []
        for n in xrange(num):
            r = random.random()
            for (i, individual) in enumerate(self):
                if r <= probs[i]:
                    new_population.append(individual)
                    break
        return new_population

    def roulette_wheel_pareto(self, pareto_set, formal_par, num):
        fitnesses = []
        fitnesses = self.create_pareto_fitness_dict(pareto_set).keys()
        total_fit = float(sum(fitnesses))
        rel_fitness = [f/total_fit for f in fitnesses]
        probs = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
        new_population = []
        for n in xrange(num):
            r = random.random()
            for (i, individual) in enumerate(formal_par):
                if r <= probs[i]:
                    new_population.append(individual)
                    break
        return new_population

    def list_repr(self):
        temp = []
        for j in self:
            temp.append(j.list_repr())
        return temp

    def choose_pareto(self):
        temp = []
        pareto_set = []
        for j in self:
            temp.append(j.list_repr())
        pareto_set = self.utility.non_dominated(temp)
        return pareto_set

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

    def create_pareto_fitness_dict(self, pareto_set):
        pareto_hardness_dict = {}
        for pareto_ind in pareto_set:
            count = 0.0
            for ind in self.list_repr():
                if self.utility.dominates(pareto_ind, ind):
                    count += 1
            pareto = count / (self.__len__()+1)
            pareto_hardness_dict[pareto] = pareto_ind
        return pareto_hardness_dict

    def create_population_fitness_dict(self, pareto_set):
        population_fitness_dict = {}
        par_fit_list = self.create_pareto_fitness_dict(pareto_set).keys()
        for ind, ind_real in zip(self.list_repr(), self):
            sum_fit = 1.0
            for pareto_ind, fit in zip(pareto_set, par_fit_list):
                if self.utility.dominates(pareto_ind, ind):
                    sum_fit += fit
            population_fitness_dict[1.0/sum_fit] = ind_real
        return population_fitness_dict


# start with a population of 10 random organisms
ph = TestOrganismPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    while True:
        pareto = ph.choose_pareto()
        formal_pareto = ph.pareto_formal(pareto)

        pareto_fit_dict = ph.create_pareto_fitness_dict(pareto)
        print "pareto"
        print pareto_fit_dict

        pop_fit_dict = ph.create_population_fitness_dict(pareto)
        print "pop"
        print pop_fit_dict

        pareto_size = random.randint(1,len(pareto)-1)
        pop_size = (ph.__len__()-pareto_size)

        select_from_pop = ph.roulette_wheel_pop(pareto, pop_size)
        select_from_pareto = ph.roulette_wheel_pareto(pareto, formal_pareto, pareto_size)
        mating_pool = select_from_pop+select_from_pareto
        print "mating pool"
        print mating_pool

        indexes = random.sample(set(range(len(mating_pool))), 2)
        parents = mating_pool[indexes[0]].list_repr()+mating_pool[indexes[1]].list_repr()
        print "parents"
        print parents
        children = mating_pool[indexes[0]].crossover(mating_pool[indexes[1]])
        print "children"
        print children
        mating_pool = mating_pool+list(children)
        print "after crossover"
        print mating_pool
        r = random.randint(0,len(mating_pool)-1)
        mating_pool[indexes[0]] = mating_pool[indexes[0]].mutation_pms(mating_pool[r],0.4)
        print "after mutation pms"
        print mating_pool
        print mating_pool[indexes[0]]
        mutated_pmc = mating_pool[indexes[0]].mutation_pmc()
        print "after mutation pmc"
        print mutated_pmc
        mating_pool.append(mutated_pmc)
        print "after mutation pmc"
        print mating_pool

        b = ph.best()
        if b.fitness() == 0:
            print "cracked!"
            break
        i += 1
        ph.gen()

if __name__ == '__main__':
    main()