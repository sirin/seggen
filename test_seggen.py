#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import rndPair, BitGene
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from test import utility
from collections import defaultdict

test_list = [1,0,1]
test_sentences = []
for i in open("/home/sirin/workspace/seggen/sample.txt"):
    utility.fill_sentences_list(test_sentences,utility.make_pre_steps(i))
ind_list = []
pareto_set = []

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
        Return the gene values as a list
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

# start with a population of 10 random organisms
ph = TestOrganismPopulation()

def main(nfittest=10, nkids=100):
    i = 0

    while i < 3:
        temp = []
        for j in ph:
            temp = utility.get_segments_from_individual(j.list_repr(),test_sentences)
            ind_list.append(temp)
        pop_size = len(ind_list)
        pareto_set = utility.non_dominated(ind_list)
        pareto_fitness_list = []
        pop_fitness_list = []

        for pind in pareto_set:
            count = 0
            for ind in ind_list:
                if utility.dominates(pind, ind):
                    count += 1
            pareto_fitness_list.append(count / pop_size+1)
        print pareto_fitness_list

        for ind in ind_list:
            sum = 1.0
            for pind,fit in zip(pareto_set,pareto_fitness_list):
                if utility.dominates(pind, ind):
                    sum += fit
            pop_fitness_list.append(sum)
        print pop_fitness_list

        print len(pareto_set)
        b = ph.best()
        print "generation %s: %s best=%s average=%s)" % (
        i, repr(b), b.fitness(), ph.fitness())
        #if b.fitness() == 0:
        #    print "cracked!"
        #    break
        i += 1
        ph.gen()


if __name__ == '__main__':
    main()