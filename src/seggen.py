__author__ = 'sirinsaygili'

from src.utilities.utility import Utility
import random
from cluster import *
import scipy
from datetime import datetime

pareto_hardness_dict = {}
population_fitness_dict = {}
Pmc = 0.8
Pms = 0.4
alpha = 5

def create_gene():
    if random.random() < 0.5:
        return 1
    else:
        return 0

def create_genome():
    genome = []
    for i in range(13):
        genome.append(create_gene())
    return genome

def create_population(size):
    population = []
    for i in xrange(size):
        population.append(create_genome())
    return  population

def clear_children(children):
    del children[:]
    return children

def clear_parents(parents):
    del parents[:]
    return parents

#return dict {str(list):float}
def create_pareto_fitness_dict(population, pareto_set, utility):
    count = 0.0
    for x, y in [(x,y) for x in pareto_set for y in population]:
        if utility.dominates(x, y):
            count += 1
        pareto = count / (len(population)+1)
        pareto_hardness_dict[str(x)] = pareto
    return pareto_hardness_dict

#return dict {str(list):float}
def create_population_fitness_dict(population, pareto_set, hardness, utility):
    for ind in population:
        sum_fit = 1.0
        for pareto_ind, fit in zip(pareto_set, hardness):
            if utility.dominates(pareto_ind, ind):
                sum_fit += 1.0/fit
        population_fitness_dict[str(ind)] = 1.0/(1.0 + sum_fit)
    return population_fitness_dict

def get_probability_list():
    fitness = population_fitness_dict.values()
    total_fit = float(sum(fitness))
    rel_fitness = [f/total_fit for f in fitness]
    probabilities = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
    return probabilities

    #return list
def roulette_wheel_pop(population, probabilities, num):
    new_population = []
    for n in xrange(num):
        r = random.random()
        for (i, individual) in enumerate(population):
            if r <= probabilities[i]:
                new_population.append(list(individual))
                break
    return new_population

def get_pareto_probability_list():
    hardness = pareto_hardness_dict.values()
    total_fit = float(sum(hardness))
    rel_fitness = [f/total_fit for f in hardness]
    pareto_probabilities = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
    return pareto_probabilities

#return list
def roulette_wheel_pareto(pareto_set, pareto_probabilities, num):
    new_population = []
    for n in xrange(num):
        r = random.random()
        for (i, individual) in enumerate(pareto_set):
            if r <= pareto_probabilities[i]:
                new_population.append(list(individual))
                break
    return new_population

#return two lists
def crossover(organism1, organism2):
    p = random.randint(0, len(organism1)-1)
    offspring1 = organism1[:p] + organism2[p:]
    offspring2 = organism2[:p] + organism1[p:]
    return [offspring1,offspring2]

#return list
def mutation_Pms(organism1, organism2):
    p = random.uniform(0,1)
    if p <= Pms:
        organism1 = organism2
    return organism1

#with a probability Pmc that shifts a boundary of the individual to the next sentence.
#return list
def mutation_Pmc(organism):
    p = random.uniform(0,1)
    r = random.randint(0,len(organism)-2)
    if p <= Pmc:
        organism[r], organism[r+1] = organism[r+1], organism[r]
    return organism

def aggregation(population, utility):
    agg_dict = {}
    for ind in population:
        agg_dict[str(ind)] = utility.calculate_aggregation(ind,alpha)
    return agg_dict

def reduceParetoWithClustering(pareto):
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

def reduceParetoWithSort(pareto, utility):
    agg = aggregation(pareto, utility)
    values = [x for x in agg.values()]
    values.sort()
    mean = sum(values) / float(len(values))
    reduced = [el for el in values if el >= mean]
    temp = [key for key, value in agg.items() if value in reduced]
    if len(temp) > 50:
        temp = temp[-50:]
    return [eval(a) for a in temp]

def generation():
    utility = Utility()
    population = create_population(100)
    parents = []
    children = []
    i = 0
    count = 0
    while True:
        if i == 0:
            for ind in population:
                parents.append(ind)
            pareto = utility.non_dominated(parents)
        elif i > 0:
            new_pareto = utility.non_dominated(children)
            pareto.extend(new_pareto)
            pareto = utility.non_dominated(pareto)
            if len(pareto) > len(children):
                reduced = reduceParetoWithSort(pareto, utility)
                del pareto[:]
                pareto = reduced
            parents = clear_parents(parents)
            parents = [par for par in children]
            children = clear_children(children)


        #ga operator: selection (roulette wheel)
        pareto_quota = random.randint(1, len(pareto))
        pop_quota = (len(parents)-pareto_quota)
        create_pareto_fitness_dict(population, pareto, utility)
        create_population_fitness_dict(population, pareto, pareto_hardness_dict.values(), utility)
        pop_probabilities = get_probability_list()
        pareto_probabilities = get_pareto_probability_list()
        mating_pool = roulette_wheel_pop(population, pop_probabilities, pop_quota)
        selected_from_pareto = roulette_wheel_pareto(pareto, pareto_probabilities, pareto_quota)
        mating_pool.extend(selected_from_pareto)

        #ga operator: crossover
        for j in range(0,30):
            indexes = random.sample(set(range(len(mating_pool))), 2)
            children.extend(crossover(mating_pool[indexes[0]], mating_pool[indexes[1]]))

        #ga operator: mutation
        rand_indexes = random.sample(set(range(len(children))), 2)
        children[rand_indexes[0]] = mutation_Pms(children[rand_indexes[0]], children[rand_indexes[1]])
        mutated_pmc = mutation_Pmc(children[rand_indexes[0]])
        children.append(mutated_pmc)
        agg_val = aggregation(pareto, utility)

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

        print "pareto archive count %d" % len(pareto)
        i += 1

if __name__ == '__main__':
    print "Running Test..."
    print datetime.now()
    generation()
    print datetime.now()