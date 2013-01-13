#! /usr/bin/env python
__author__ = 'sirin'

from pygene.gene import BitGene
from pygene.organism import Organism
from pygene.population import Population
from test.utility import Utility
import random
from cluster import *
import scipy
from datetime import datetime

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
        pareto_set = TestOrganismPopulation.utility.non_dominated(my_list)
        return pareto_set

    #return dict {str(list):float}
    def create_pareto_fitness_dict(self, population, pareto_set):
        pareto_hardness_dict = {}
        for pareto_ind in pareto_set:
            if type(pareto_ind) != type(list()):
                pareto_ind = list(pareto_ind)
            count = 0.0
            if type(population) != type(list()):
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
        if type(population) != type(list()):
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
                    new_population.append(list(individual))
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
                    new_population.append(list(individual))
                    break
        return new_population

    #return two lists
    def crossover(self, organism1, organism2):
        p = random.randint(0, len(organism1)-1)
        offspring1 = organism1[:p] + organism2[p:]
        offspring2 = organism2[:p] + organism1[p:]
        return [offspring1,offspring2]

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

    def aggregation(self, individual_list, alpha):
        agg_dict = {}
        for indiv in individual_list:
            agg_dict[str(indiv)] = TestOrganismPopulation.utility.calculate_aggregation(indiv,alpha)
        return agg_dict

    def reduceParetoWithClustering(self, pareto):
        reduced = []
        cl = HierarchicalClustering(pareto,lambda x,y: scipy.spatial.distance.euclidean(x,y))
        cl.setLinkageMethod('average')
        for lev in cl.getlevel(4):
            if len(lev)>1:
                if len(lev) % 2 == 0:
                    reduced.append(lev[len(lev)/2])
                else:
                    reduced.append(centroid(lev))
            else:
                reduced.append(lev)
        return reduced

    def reduceParetoWithSort(self, pareto):
        agg = self.aggregation(pareto, 5)
        values = [x for x in agg.values()]
        values.sort()
        mean = sum(values) / float(len(values))
        reduced = [el for el in values if el >= mean]
        temp = [key for key, value in agg.items() if value in reduced]
        if len(temp) > 50:
            temp = temp[-50:]
        return [eval(a) for a in temp]

class TestGene(BitGene):

    mutProb = 0.1
    mutAmt = 10.0

    randMin = 0x0
    randMax = 0xff

    def __add__(self, other):
        return (self.value + other.value) / 2

# generate a genome, one gene for each binary in the list
genome = {}
for i in range(13):
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
    initPopulation = 50
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

# start with a population of 100 random organisms
ph = TestOrganismPopulation()

def main(nfittest=10, nkids=100):
    i = 0
    flow = Flow()
    count = 0
    while True:
        if i == 0:
            for ind in ph:
                flow.parents.append(ind.list_repr())
            pareto = flow.choose_pareto(flow.get_parents())
        elif i > 0:
            new_pareto = flow.choose_pareto(flow.get_children())
            pareto = pareto + new_pareto
            pareto = TestOrganismPopulation.utility.non_dominated(pareto)
            if len(pareto) > len(flow.children):
                reduced = flow.reduceParetoWithSort(pareto)
                del pareto[:]
                pareto = reduced
            flow.clear_parents()
            flow.parents = [par for par in flow.get_children()]
            flow.clear_children()

        pareto_size = random.randint(1,len(pareto))
        pop_size = (len(flow.get_parents())-pareto_size)


        #ga operator: selection
        select_from_pop = flow.roulette_wheel_pop(flow.get_parents(), pareto, pop_size)
        select_from_pareto = flow.roulette_wheel_pareto(flow.get_parents(), pareto, pareto_size)
        mating_pool = select_from_pop+select_from_pareto


        #ga operator: crossover
        for j in range(0,30):
            indexes = random.sample(set(range(len(mating_pool))), 2)
            flow.children.extend(flow.crossover(mating_pool[indexes[0]], mating_pool[indexes[1]]))

        #ga operator: mutation
        rand_indexes = random.sample(set(range(len(flow.children))), 2)
        flow.children[rand_indexes[0]] = flow.mutation_pms(flow.children[rand_indexes[0]], flow.children[rand_indexes[1]], 0.4)
        mutated_pmc = flow.mutation_pmc(flow.children[rand_indexes[0]])
        flow.children.append(mutated_pmc)
        agg_val = flow.aggregation(pareto, 5)

        if i == 0:
            copy_pareto = pareto
            print "%d. step pareto archive" % (i+1)
            #for a in agg_val.items():
                #print a
        else:
            if copy_pareto != pareto:
                copy_pareto = pareto
                count = 0
                #print "%d. step pareto archive, count %d" % ((i+1),count)
                #for b in agg_val.items():
                    #print b
            else:
                count+=1
                #print "%d. step pareto archive, count %d" % ((i+1),count)
                #for c in agg_val.items():
                    #print c
            if count >= 20:
                print "result pareto archive at %d. step" %(i+1)
                for d in agg_val.items():
                    print d
                break

        print "pareto size %d" % len(pareto)
        i += 1

if __name__ == '__main__':
    print "Running Test..."
    print datetime.now()
    main()
    print datetime.now()