#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import rndPair, BitGene
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from test.utility import Utility
from random import choice

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

    initPopulation = 10
    species = TestOrganism
    # cull to this many children after each generation
    childCull = 10

    # number of children to create after each generation
    childCount = 40

    def override_best(self,list):
        list.sort()
        return list[0]

# start with a population of 10 random organisms
ph = TestOrganismPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    utility = Utility()
    while True:
        temp = []
        individuals = []
        for j in ph:
            individuals.append(j.list_repr())

        pop_size = len(individuals)
        pareto_set = utility.non_dominated(individuals)
        pareto_set_official =[]
        for x in pareto_set:
            pareto_set_official.append(' '.join(str(elem) for elem in x))
        #print pareto_set_official[0]

        pareto_hardness_list = []
        pareto_hardness_dict = {}
        population_strength_list = []
        population_strength_dict = {}

        #print "population: %s" % ph
        #print "pareto set: %s" % pareto_set
        print "selected from pareto set: %s" % choice(pareto_set_official)

        for pind, preal in zip(pareto_set, pareto_set_official):
            count = 0.0
            for ind in individuals:
                if utility.dominates(pind, ind):
                    count += 1
            pareto = count / (pop_size+1)
            pareto_hardness_list.append(pareto)
            pareto_hardness_dict[pareto] = preal

        #print "pareto hardness list: %s" % pareto_hardness_list
        #print "pareto hardness dict: %s" % pareto_hardness_dict

        for ind, ireal in zip(individuals,ph):
            sum_fit = 1.0
            for pind, fit in zip(pareto_set,pareto_hardness_list):
                if utility.dominates(pind, ind):
                    sum_fit += fit
            population_strength_list.append(1.0/sum_fit)
            population_strength_dict[1.0/sum_fit] = ireal

        #print "population fitness list: %s" % population_strength_list
        #print "population fitness dict: %s" % population_strength_dict
        t = choose_best(population_strength_dict)
        print "selected from population: %s" % t[1]
        b = ph.best()

        #print "Generation %s: %s Best=%s Average=%s)" % (
        #i, repr(b), b.fitness(), ph.fitness())
        if b.fitness() == 0:
            print "cracked!"
            break
        del individuals[:]
        i += 1
        ph.gen()

if __name__ == '__main__':
    main()