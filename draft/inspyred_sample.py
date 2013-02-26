import random
import time
import inspyred
from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
from numpy import zeros,dot
from numpy.linalg import norm
from itertools import combinations
from datetime import datetime

refined_sentences = []
def fill_sentences_list(all_sentences,sentence):
    all_sentences.append(sentence)
    return all_sentences

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

def clear_stopwords(words, stopwords):
    for stopword in stopwords:
        words = filter(lambda x:x!=stopword, words)
    return words

def make_pre_steps(text):
    replacement_chars = {
        "1" : " ","2" : " ","3" : " ","4" : " ","5" : " ","6" : " ","7" : " ","8" : " ","9" : " ","0" : " ",
        "\n" : " ",
        "/t" : " ",
        "`" : " ",
        ":" : " ",
        "." : " ",
        "," : " ",
        "?" : " ",
        "$" : " ",
        "+" : " ",
        "*" : " ",
        "!" : " ",
        "^" : " ",
        "%" : " ",
        "'" : " ",
        '"' : " ",
        '&' : " ",
        '{' : ' ',
        '}' : ' ',
        '[' : ' ',
        ']' : ' ',
        '@' : ' ',
        '/' : ' ',
        '\\' : ' ',
        '~' : ' ',
        '|' : ' ',
        ';' : ' ',
        '_' : ' ',
        "-" : " "
    }
    stopwords = []
    porter = PorterStemmer()
    for i in open("/Users/sirinsaygili/workspace/seggen/stopwords.txt"):
        stopwords.append(i.replace("\n",""))
    text = replace_all(text, replacement_chars)
    words = word_tokenize(text)
    words = [word.lower() for word in words]
    words = clear_stopwords(words, stopwords)
    words = [porter.stem(word) for word in words]
    return words

def refine_text():
    for i in open("/Users/sirinsaygili/workspace/seggen/N1.txt"):
        fill_sentences_list(refined_sentences,make_pre_steps(i))
    return refined_sentences

def add_word(all_words, word):
    all_words.setdefault(word,0)
    all_words[word] += 1

def get_segments_from_individual(individual, sentences):
    temp = []
    segments = []
    for i, j in zip(individual,range(len(sentences))):
        temp.append(sentences[j])
        if i == 1:
            fill_sentences_list(segments,temp)
            temp = []
    if len(sentences) == len(individual)+1:
        temp.append(sentences[-1])
        fill_sentences_list(segments,temp)
        temp = []
    return segments

# used by compare method
def doc_vec(doc, key_idx):
    v = zeros(len(key_idx))
    for word in doc:
        keydata = key_idx.get(word, None)
        if keydata:
            v[keydata[0]] = 1
    return v

# used by calculate_cohesion method
def compare(doc1, doc2):
    all_words = dict()
    for w in doc1:
        add_word(all_words,w)
    for w in doc2:
        add_word(all_words,w)
    key_idx = dict() # key-> ( position, count )
    keys = all_words.keys()
    keys.sort()
    for i in range(len(keys)):
        key_idx[keys[i]] = (i,all_words[keys[i]])
    del keys
    del all_words

    v1=doc_vec(doc1,key_idx)
    v2=doc_vec(doc2,key_idx)
    return float(dot(v1,v2) / (norm(v1) * norm(v2)))

# used by calculate_sim_of_individual
def calculate_cohesion(seg):
    sum_seg = 0.0
    couple_len = 0
    if len(seg) > 1:
        for prv, nxt in zip(seg, seg[1:]):
            sum_seg +=  compare(prv,nxt)
            couple_len += 1
        return sum_seg/couple_len
    else:
        return 1

# used by compare_similarity method
def calculate_sim_of_individual(individual):
    sim = 0.0
    if len(individual) > 1:
        for i in individual:
            sim +=  calculate_cohesion(i)
        return sim/len(individual)
    else:
        return 1

# used by calculate_dissimilarity
def calculate_simseg(segment1, segment2):
    divisor = len(segment1) * len(segment2)
    sum_sim = 0.0
    for x, y in [(x,y) for x in segment1 for y in segment2]:
        sum_sim += compare(x,y)
    return sum_sim / divisor

# used by compare_dissimilarity
def calculate_dissimilarity(segment_list):
    dissimilarity = 0.0
    compare_len = 0
    if len(segment_list) > 1:
        for prv, nxt in zip(segment_list, segment_list[1:]):
            dissimilarity += calculate_simseg(prv,nxt)
            compare_len += 1
        return (1.0 -(dissimilarity / compare_len))
    else:
        return 0 #TODO check this point and fix it!

# used by non_dominated and dominates methods
def compare_similarity(first, second):
    return calculate_sim_of_individual(first) >= calculate_sim_of_individual(second)

# used by non_dominated and dominates methods
def compare_dissimilarity(first, second):
    return calculate_dissimilarity(first) >= calculate_dissimilarity(second)

def non_dominated(ind_list):
    result = []
    for combo in combinations(ind_list, 2):
        x_sentence = get_segments_from_individual(combo[0],refined_sentences)
        y_sentence = get_segments_from_individual(combo[1],refined_sentences)
        if compare_similarity(x_sentence,y_sentence) and compare_dissimilarity(x_sentence,y_sentence):
            result.append(combo[0])
    return remove_duplicate(result)

    # used by non_dominated method
def remove_duplicate(seq):
    seq.sort()
    last = seq[-1]
    for i in range(len(seq)-2, -1, -1):
        if last == seq[i]:
            del seq[i]
        else:
            last = seq[i]
    return seq

def dominates(x, y):
    x_sentence = get_segments_from_individual(x,refined_sentences)
    y_sentence = get_segments_from_individual(y,refined_sentences)
    return compare_similarity(x_sentence, y_sentence) and compare_dissimilarity(x_sentence, y_sentence)

def generate_binary(random, args):
    bits = args.get('num_bits', 10)
    return [random.choice([0, 1]) for i in range(bits)]

def evaluate_fitness(candidates, args):
    archive = args['_ec'].archive
    #calculate the hardness/fitness of each archive solution.
    for a in archive:
        count = 0
        for c in candidates:
            individual = str(a).split(" : ")[0]
            if dominates(individual, c):
                count += 1
        hardness = float(count) / (len(candidates) + 1)
        a.fitness = 1.0 / hardness

    #calculate the fitness of the population.
    fitness = []
    for c in candidates:
        total_hardness = 0
        for a in archive:
            binary_part = str(a).split(" : ")[0]
            if dominates(binary_part, c):
                total_hardness += 1.0 / a.fitness
        fitness.append(1.0 / (1 + total_hardness))
    return fitness

def main(prng=None, display=False):
    rand = random.Random()
    rand.seed(int(time.time()))
    refine_text()
    ga = inspyred.ec.emo.ec.GA(rand)
    ga.observer = inspyred.ec.emo.ec.observers.stats_observer
    ga.archiver = inspyred.ec.emo.ec.archivers.best_archiver
    ga.selector = inspyred.ec.emo.ec.selectors.fitness_proportionate_selection
    ga.variator = [inspyred.ec.emo.ec.variators.n_point_crossover,
                   inspyred.ec.emo.ec.variators.bit_flip_mutation]
    ga.replacer = inspyred.ec.emo.ec.replacers.generational_replacement
    ga.terminator = inspyred.ec.emo.ec.terminators.diversity_termination
    final_pop = ga.evolve(evaluator=evaluate_fitness,
        generator=generate_binary,
        max_evaluations=10000,
        num_elites=50,
        pop_size=100,
        num_bits=13)
    if display:
        final_arc = ga.archive
        print('Best Solutions: \n')
        for f in final_arc:
            print(f)


if __name__ == '__main__':
    main(display=True)