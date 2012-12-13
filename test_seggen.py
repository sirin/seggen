#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import rndPair, BitGene
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from test.utility import Utility
from random import choice
import random

test_list = [1,0,1]
pareto_set = []

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


class TestOrganism(MendelOrganism):
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a string
        """
        bits = []
        for k in xrange(self.numgenes):
            n = self[k]
            bits.append(n)
        return " ".join(map(str, bits))

    def list_repr(self):
        """
        Return the gene values as a list
        """
        bits = []
        for k in xrange(self.numgenes):
            n = self[k]
            bits.append(n)
        return bits

    def fitness(self):
        """
        calculate fitness, as the absolute value of the
        subtract of each bit gene from the
        corresponding bit of the target list
        """
        diffs = 0
        for i in xrange(self.numgenes):
            x0 = test_list[i]
            x1 = self[i]
            diffs += abs(x0 - x1)
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
    #select only one result
    def roulette_wheel(self, fit_dict, pareto_set):
        total_fix = sum(self.create_population_fitness_dict(pareto_set).keys())
        pick = random.uniform(0, total_fix)
        current = 0
        for key, value in fit_dict.items():
            current += key
            if current > pick:
                return value

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
        t = []
        t = ph.choose_pareto()
        #print t
        k = []
        k = ph.pareto_list_to_str(t)
        #print k
        n = {}
        n = ph.create_pareto_fitness_dict(t)
        print n
        #print n.keys()
        z = {}
        z = ph.create_population_fitness_dict(t)
        print z
        s = ph.roulette_wheel(z, t)
        print s
        #print "Generation %s: %s Best=%s Average=%s)" % (
        #i, repr(b), b.fitness(), ph.fitness())
        b = ph.best()
        if b.fitness() == 0:
            print "cracked!"
            break
        i += 1
        ph.gen()

if __name__ == '__main__':
    main()