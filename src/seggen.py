__author__ = 'sirinsaygili'

'''
This file is part of Seggen-Improve Project.

Seggen-Improve is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seggen-Improve is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seggen-Improve.  If not, see <http://www.gnu.org/licenses/>.
'''

from src.utilities.utility import Utility
import random
from cluster import *
import scipy
from datetime import datetime
from nltk.metrics import windowdiff
import sys
from random import choice

pareto_hardness_dict = {}
population_fitness_dict = {}
alpha = 5
options = ['M1','M2','C','M1C','M2C']

''' Create binary gene '''
def create_gene():
    if random.random() < 0.5:
        return 1
    else:
        return 0

''' Create genome consists of binary genes '''
def create_genome():
    genome = []
    for i in range(25):
        genome.append(create_gene())
    return genome

''' Create population consists of genome
    for given size '''
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

''' Create pareto archive strength dictionary
    consists of {individual:strength} pairs '''
def create_pareto_fitness_dict(population, pareto_set, utility):
    pareto_objective_list = utility.create_objective_value_list_of_population(pareto_set)
    pop_objective_list = utility.create_objective_value_list_of_population(population)
    count = 0.0
    for x,x_obj in zip(pareto_set,pareto_objective_list):
        for y_obj in pop_objective_list:
            if x_obj[0] >= y_obj[0] and x_obj[1] >= y_obj[1]:
                count += 1.0
        strength = float(count / (len(population)+1))
        pareto_hardness_dict[str(x)] = strength
    return pareto_hardness_dict

''' Create population fitness dictionary
    consists of {individual:fitness} pairs '''
def create_population_fitness_dict(population, pareto_set, hardness, utility):
    pareto_objective_list = utility.create_objective_value_list_of_population(pareto_set)
    pop_objective_list = utility.create_objective_value_list_of_population(population)
    for ind,pop_obj in zip(population,pop_objective_list):
        sum_fit = 1.0
        for pareto_obj, strength in zip(pareto_objective_list, hardness):
            if pareto_obj[0] >= pop_obj[0] and pareto_obj[1] >= pop_obj[1]:
                sum_fit += strength
        population_fitness_dict[str(ind)] = float(1.0/(1.0 + sum_fit))
    return population_fitness_dict

''' Utility method for roulette wheel selection '''
def get_probability_list():
    fitness = population_fitness_dict.values()
    total_fit = float(sum(fitness))
    rel_fitness = [f/total_fit for f in fitness]
    probabilities = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
    return probabilities

''' Select individuals from current population for their fitness values
    (roulette wheel) fitness proportionate selection '''
def roulette_wheel_pop(population, probabilities, num):
    new_population = []
    for n in xrange(num):
        r = random.random()
        for (i, individual) in enumerate(population):
            if r <= probabilities[i]:
                new_population.append(list(individual))
                break
    return new_population

''' Utility method for roulette wheel selection '''
def get_pareto_probability_list():
    hardness = pareto_hardness_dict.values()
    total_fit = float(sum(hardness))
    rel_fitness = [f/total_fit for f in hardness]
    pareto_probabilities = [sum(rel_fitness[:i+1]) for i in range(len(rel_fitness))]
    return pareto_probabilities

''' Select individuals from pareto archive for their fitness values
    (roulette wheel) fitness proportionate selection '''
def roulette_wheel_pareto(pareto_set, pareto_probabilities, num):
    new_population = []
    for n in xrange(num):
        r = random.random()
        for (i, individual) in enumerate(pareto_set):
            if r <= pareto_probabilities[i]:
                new_population.append(list(individual))
                break
    return new_population

''' Single point crossover '''
def crossover(organism1, organism2):
    p = random.randint(0, len(organism1)-1)
    offspring1 = organism1[:p] + organism2[p:]
    offspring2 = organism2[:p] + organism1[p:]
    return [offspring1,offspring2]

''' Two points keep boundary crossover '''
def crossover_keep_boundary(organism1, organism2):
    indices1 = [item for item in range(len(organism1)) if organism1[item] == 1]
    indices2 = [item for item in range(len(organism2)) if organism2[item] == 1]
    common = list(set(indices1) & set(indices2))
    if len(common)>=2:
        points = random.sample(common,2)
        points.sort()
        offspring1 = organism1[:points[0]] + organism2[points[0]:points[1]]+ organism1[points[1]:]
        offspring2 = organism2[:points[0]] + organism1[points[0]:points[1]]+ organism2[points[1]:]
    elif len(common) == 1:
        r = random.randint(0, len(organism1)-1)
        if r >= common[0]:
            offspring1 = organism1[:common[0]] + organism2[common[0]:r]+ organism1[r:]
            offspring2 = organism2[:common[0]] + organism1[common[0]:r]+ organism2[r:]
        else:
            offspring1 = organism1[:r] + organism2[r:common[0]]+ organism1[common[0]:]
            offspring2 = organism2[:r] + organism1[r:common[0]]+ organism2[common[0]:]
    else:
        pick = random.sample(range(len(organism1)),2)
        pick.sort()
        offspring1 = organism1[:pick[0]] + organism2[pick[0]:pick[1]]+ organism1[pick[1]:]
        offspring2 = organism2[:pick[0]] + organism1[pick[0]:pick[1]]+ organism2[pick[1]:]
    return [offspring1,offspring2]

def percentage(whole, ratio):
    return (whole * ratio)/100

def find_nth_overlapping(haystack, needle, n):
    start = haystack.index(needle)
    while start >= 0 and n > 1:
        start = haystack.index(needle, start+1)
        n -= 1
    return start

''' One point crossover that provides cutting at the same boundary count'''
def crossover_same_boundary_count(organism1, organism2):
    count1 = percentage(organism1.count(1),40)
    count2 = percentage(organism2.count(1),40)
    ind1 = find_nth_overlapping(organism1,1,count1)
    ind2 = find_nth_overlapping(organism2,1,count2)
    if abs(ind1-ind2) <= 3:
        cross = max(ind1,ind2)
        offspring1 = organism1[:cross] + organism2[cross:]
        offspring2 = organism2[:cross] + organism1[cross:]
        return [True,offspring1,offspring2]
    else:
        return [False, organism1,organism2]

''' One point crossover that merges two parents and cut'''
def crossover_merge(organism1, organism2):
    merged = []
    merged = [x if x == y else max(x,y) for x, y in zip(organism1,organism2)]
    avg_boundary = (merged.count(1))/2
    indices = [item for item in range(len(merged)) if merged[item] == 1]
    pick = random.sample(indices,avg_boundary)
    for i in pick:
        merged[i] = 0
    return merged


''' A kind of mutation based on with a probability Pms
    replaced by other individual '''
def mutation_Pms(organism1, organism2, Pms):
    p = random.uniform(0,1)
    if p <= Pms:
        organism1 = organism2
    return organism1

''' A kind of mutation based on with a probability Pmc that
    do bit flip on given individual '''
def mutation_Pmc(organism, Pmc):
    p = random.uniform(0,1)
    r = random.randint(0,len(organism)-2)
    if p <= Pmc:
        organism[r], organism[r+1] = organism[r+1], organism[r]
    return organism

''' A kind of mutation based on with a probability P that
    do shift boundary to next sentence on given individual '''
def mutation_boundary_shift(organism, Pbs):
    p = random.uniform(0,1)
    if p <= Pbs:
        indices = [item for item in range(len(organism)) if organism[item] == 1]
        if len(indices)>=2:
            points = random.sample(indices,2)
            if points[0]<len(organism)-1 and points[1]<len(organism)-1:
                organism[points[0]], organism[points[0]+1] = 0, 1
                organism[points[1]], organism[points[1]+1] = 0, 1
            elif points[0] != len(organism)-1:
                organism[points[0]], organism[points[0]+1] = 0, 1
            elif points[1] != len(organism)-1:
                organism[points[1]], organism[points[1]+1] = 0, 1
        elif len(indices) == 1:
            if indices[0] != len(organism)-1:
                organism[indices[0]], organism[indices[0]+1] = 0, 1
        else:
            pick = random.randint(0,len(organism)-1)
            organism[pick] = 1
    return organism

''' A kind of mutation based on with a probability P that
    add a boundary into given individual '''
def mutation_add_boundary(organism, Pbs):
    p = random.uniform(0,1)
    if p <= Pbs:
        indices = [item for item in range(len(organism)) if organism[item] == 0]
        pick = random.sample(indices,1)
        organism[pick[0]] = 1
    return organism

''' Trial aggregation function it would be improved '''
def aggregation(population, utility):
    agg_dict = {}
    for ind in population:
        agg_dict[str(ind)] = utility.calculate_aggregation(ind,alpha)
    return agg_dict

''' Trial weighted aggregation function it would be improved '''
def weighted_aggregation(population, utility):
    w_agg_dict = {}
    for ind in population:
        w_agg_dict[str(ind)] = utility.calculate_weighted_aggregation(ind,alpha)
    return w_agg_dict

''' Reduce pareto archive size when it over given limit based on
    hierarchical clustering method '''
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

''' Reduce pareto archive size when it over given limit based on
    sorting and picking up upper part of average value '''
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

def get_diff(basic, weighted):
    diff = {}
    for i_val, j_val, j in zip(basic.values(),weighted.values(),weighted.keys()):
        diff[j] = abs(i_val-j_val)
    for a, v in zip(diff.keys(),diff.values()):
        if v > 0.79:
            del diff[a]
    return diff

def pick_better_results(population,utility):
    result = []
    for i in population:
        if utility.calculate_aggregation(i,alpha) >= 4.9:
            result.append(i)
    return result

def calculate_global_quality(population, utility):
    samples = random.sample(population, percentage(len(population), 10))
    agg = aggregation(samples,utility)
    total = [i for i in agg.values()]
    return sum(total)/len(total)

''' Main genetic algorithm parts of code; create population,
    create pareto-archive, apply genetic algorithm operators,
    update pareto-archive '''
def generation(code_type, input_type, index):
    utility = Utility()
    population = create_population(250)
    parents = []
    children = []
    i = 0
    same_count = 0
    control_group = []
    Pms = 0.8
    Pmc = 0.4
    Pbs = 0.1
    prob_list = []
    quality = []
    diff = []
    option = ''
    while i < 5000:
        if i == 0:
            for ind in population:
                parents.append(ind)
            pareto = utility.non_dominated(parents)
            control_group = pareto[:]
        elif i > 0:
            new_pareto = utility.non_dominated(children)
            pareto.extend(new_pareto)
            pareto = utility.non_dominated(pareto)
            if len(pareto) > len(children):
                reduced = reduceParetoWithSort(pareto, utility)
                del pareto[:]
                pareto = reduced[:]
            parents = clear_parents(parents)
            parents = [par for par in children]
            children = clear_children(children)
            if control_group != pareto:
                del control_group[:]
                control_group = pareto[:]
                same_count = 0
            else:
                same_count += 1
            if same_count >= 40:
#                f = open("/Users/sirinsaygili/workspace/seggen/results/"+code_type+"_"+input_type+"_"+str(index)+".txt","w")
#                print "%s type,input %s, result at %d. generation" %(code_type, input_type, (i+1))
#                reference = "0000000001000000000100001000010000001000000000000"
#                for key in pick_better_results(pareto,utility):
#                    s = ''.join(str(x) for x in key)
#                    r = [key,windowdiff(reference,s,9)]
#                    f.write(str(r)+"\n")
#                f.write(str("program finished at %d. generation" %(i+1)))
#                f.close()
                for t in agg_val.items():
                    print t
                break

        pareto_quota = random.randint(1, len(pareto))
        pop_quota = (len(parents)-pareto_quota)
        create_pareto_fitness_dict(population, pareto, utility)
        create_population_fitness_dict(population, pareto, pareto_hardness_dict.values(), utility)
        pop_probabilities = get_probability_list()
        pareto_probabilities = get_pareto_probability_list()

        #ga operator: selection (roulette wheel)
        mating_pool = roulette_wheel_pop(population, pop_probabilities, pop_quota)
        selected_from_pareto = roulette_wheel_pareto(pareto, pareto_probabilities, pareto_quota)
        mating_pool.extend(selected_from_pareto)

        #ga operator: crossover
        for j in range(0,60):
            if len(mating_pool) >= 2:
                indexes = random.sample(range(len(mating_pool)), 4)
                if option == 'C' or 'M1C' or 'M2C':
                    created = crossover_merge(mating_pool[indexes[2]], mating_pool[indexes[3]])
                    children.append(created)
                    crossed = crossover_same_boundary_count(mating_pool[indexes[0]], mating_pool[indexes[1]])
                    if crossed[0] is True:
                        children.extend(crossed[1:])
                    else:
                        children.extend(crossover_keep_boundary(mating_pool[indexes[0]], mating_pool[indexes[1]]))
                else:
                    children.extend(crossover(mating_pool[indexes[0]], mating_pool[indexes[1]]))
            else:
                print "sampler larger than %d" % len(mating_pool)
                for k in agg_val.items():
                    print k
                break

        #ga operator: mutation
        rand_indexes = random.sample(set(range(len(children))), 2)
        if option == 'M1' or 'M2' or 'M1C' or 'M2C':
            mutated_boundary_shift = mutation_boundary_shift(children[rand_indexes[0]], Pbs)
            children.append(mutated_boundary_shift)
            mutated_boundary_add = mutation_add_boundary(children[rand_indexes[0]], Pbs)
            children.append(mutated_boundary_add)
        else:
            children[rand_indexes[0]] = mutation_Pms(children[rand_indexes[0]], children[rand_indexes[1]], Pms)
            mutated_pmc = mutation_Pmc(children[rand_indexes[0]], Pmc)
            children.append(mutated_pmc)

        agg_val = aggregation(pareto, utility)
        if option == 'M2' or 'M2C':
            if i == 9:
                values = [x for x in agg_val.values()]
                mean_val = sum(values) / float(len(values))
                prob_list.append(mean_val)
            if i>0 and i%10 == 0:
                values = [x for x in agg_val.values()]
                mean = sum(values) / float(len(values))
                if mean < prob_list[-1] and Pbs<=0.8:
                    Pbs+=0.05
                prob_list.append(mean)

        if i == 9:
            quality.append(calculate_global_quality(parents,utility))
        if i>0 and i%10 == 0:
            instant = calculate_global_quality(parents,utility)
            if instant < quality[-1]:
                option = choice(options)
            quality.append(instant)
            print quality[-1]
            print option

        if i == 4999:
            for t in agg_val.items():
                print t
        i += 1

''' Main function calls generation method '''
if __name__ == '__main__':
    print "Running Test"
    print datetime.now()
    #mut prob degisikligi bir sonraki adimda gerceklenecek
    generation("Mixed","N2",0)
    print datetime.now()