__author__ = 'sirinsaygili'


from pyevolve import G1DList
from pyevolve import Initializators
from pyevolve import Mutators
from pyevolve import Selectors, Statistics
from pyevolve import Crossovers
from pyevolve import GSimpleGA
from test.utility import Utility
from inspyred import ec

# choose pareto
def fitness(chromosome):
    score = 0
    for value in chromosome:
        if value==0:
            score += 1
    return score

def run_main():
    # Genome instance
    genome = G1DList.G1DList(13)
    genome.setParams(rangemin=0, rangemax=1)
    genome.initializator.set(Initializators.G1DListInitializatorInteger)
    genome.crossover.set(Crossovers.G1DListCrossoverSinglePoint)
    genome.mutator.set(Mutators.G1DListMutatorIntegerBinary)

    # The evaluator function (objective function)
    genome.evaluator.set(fitness)

    # Genetic Algorithm Instance
    ga = GSimpleGA.GSimpleGA(genome)
    ga.selector.set(Selectors.GRouletteWheel)
    ga.setGenerations(4000)
    ga.setCrossoverRate(0.9)
    ga.setPopulationSize(100)
    ga.setMutationRate(0.03)

    ga.evolve(20)

    # Best individual
    best = ga.bestIndividual()
    print "\nBest individual score: %.2f" % (best.score,)
    print best


if __name__ == "__main__":
    run_main()
