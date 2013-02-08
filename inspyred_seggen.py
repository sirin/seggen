__author__ = 'sirinsaygili'

from random import Random
from time import time
import inspyred

def main(prng=None, display=False):
    if prng is None:
        prng = [[1,1,0,0,0,0,0,1,0,0,1,0,0],[0,0,0,0,0,1,0,0,0,0,1,0,0],[0,0,0,1,0,0,0,0,0,0,0,1,1],[0,0,0,1,0,0,0,1,0,0,0,1,0]]

    @inspyred.ec.evaluators.evaluator
    def my_evaluator(candidate, args):
        obj1 = 1 # Calculate objective 1
        obj2 = 2 # Calculate objective 2
        obj3 = 3 # Calculate objective 3
        return inspyred.ec.emo.Pareto([obj1, obj2, obj3])

    #problem = inspyred.benchmarks.emo.Pareto(prng)
    ea = inspyred.ec.emo.Pareto(prng)
    ea.selector = inspyred.ec.selectors.fitness_proportionate_selection
    ea.variator = [inspyred.ec.variators.n_point_crossover,
                   inspyred.ec.variators.bit_flip_mutation]
    ea.replacer = inspyred.ec.replacers.generational_replacement
    ea.terminator = inspyred.ec.terminators.generation_termination
    final_pop = inspyred.ec.evaluators.evaluator(
        evaluator=my_evaluator,
        pop_size=100,
        tournament_size=7,
        num_selected=2,
        max_generations=300,
        mutation_rate=0.2)

    if display:
        best = max(final_pop)
        print('Best Solution: \n{0}'.format(str(best)))
    return ea

if __name__ == '__main__':
    main(display=True)