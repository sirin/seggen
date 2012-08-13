#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import FloatGene, IntGene, rndPair
from pygene.gamete import Gamete
from pygene.organism import Organism, MendelOrganism
from pygene.population import Population
from random import random, randint


test_list = [1,0,1,1,0,1,1]

class TestGene(IntGene):

    mutProb = 0.1
    mutAmt = 10.0

    randMin = 0x0
    randMax = 0xff
# generate a genome, one gene for each binary in the list
genome = {}
for i in range(len(test_list)):
    genome[str(i)] = TestGene

class TestOrganism(MendelOrganism):
    genome = genome

    def __repr__(self):
        """
        Return the gene values as a list TODO: needs improvement representation!
        """
        chars = []
        for k in xrange(self.numgenes):
            n = self[k]
            c = chr(n)
            chars.append(c)
        return ''.join(chars)

    def fitness(self):
        """
        calculate fitness, as the sum of the squares
        of the distance of each char gene from the
        corresponding char of the target string
        """
        diffs = 0
        guess = str(self)
        for i in xrange(self.numgenes):
            x0 = test_list[i]
            x1 = ord(guess[i])
            diffs += (x1 - x0) ** 2
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
    while True:
        b = ph.best()
        print "generation %s: %s best=%s average=%s)" % (
        i, repr(b), b.fitness(), ph.fitness())
        if b.fitness() <= 0:
            print "cracked!"
            break
        i += 1
        ph.gen()


if __name__ == '__main__':
    main()