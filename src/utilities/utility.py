#! /usr/bin/env python
__author__ = 'sirin'

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

from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
from numpy import zeros,dot
from numpy.linalg import norm
import numpy

''' This class provides some utilities are
    to clear words, to tokenize and to stem'''
class Pre:
    def fill_sentences_list(self, all_sentences,sentence):
        all_sentences.append(sentence)
        return all_sentences

    def replace_all(self, text, dic):
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return text

    def clear_stopwords(self, words, stopwords):
        for stopword in stopwords:
            words = filter(lambda x:x!=stopword, words)
        return words

    def make_pre_steps(self, text):
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
        for i in open("/Users/sirinsaygili/workspace/seggen/src/stopwords.txt"):
            stopwords.append(i.replace("\n",""))
        text = self.replace_all(text, replacement_chars)
        words = word_tokenize(text)
        words = [word.lower() for word in words]
        words = self.clear_stopwords(words, stopwords)
        words = [porter.stem(word) for word in words]
        return words

''' This class provides all similarity and dissimilarity
    calculation between sentences '''
class Utility:
    starts = {}
    ends = {}
    running_times = {}

    refined_sentences = []
    def __init__(self):
        pre = Pre()
        for i in open("/Users/sirinsaygili/workspace/seggen/src/N1.txt"):
            pre.fill_sentences_list(self.refined_sentences,pre.make_pre_steps(i))

    def add_word(self, all_words, word):
        all_words.setdefault(word,0)
        all_words[word] += 1

    '''Arrange sentence array regarding to given individual '''
    def get_segments_from_individual(self, individual, sentences):
        pre = Pre()
        temp = []
        segments = []
        for i, j in zip(individual,range(len(sentences))):
            temp.append(sentences[j])
            if i == 1:
                pre.fill_sentences_list(segments,temp)
                temp = []
        if len(sentences) == len(individual)+1:
            temp.append(sentences[-1])
            pre.fill_sentences_list(segments,temp)
            temp = []
        return segments

    '''utility method used by compare method '''
    def doc_vec(self, doc, key_idx):
        v = zeros(len(key_idx))
        for word in doc:
            keydata = key_idx.get(word, None)
            if keydata:
                v[keydata[0]] = 1
        return v

    ''' simple comparator method (cosine similarity)
        used by calculate_cohesion method '''
    def compare(self, doc1, doc2):
        all_words = dict()
        for w in doc1:
            self.add_word(all_words,w)
        for w in doc2:
            self.add_word(all_words,w)
        key_idx = dict() # key-> ( position, count )
        keys = all_words.keys()
        keys.sort()
        for i in range(len(keys)):
            key_idx[keys[i]] = (i,all_words[keys[i]])
        del keys
        del all_words

        v1=self.doc_vec(doc1,key_idx)
        v2=self.doc_vec(doc2,key_idx)
        return float(dot(v1,v2) / (norm(v1) * norm(v2)))

    ''' Calculate internal cohesion value between segments
        used by calculate_sim_of_individual '''
    def calculate_cohesion(self, seg):
        sum_seg = 0.0
        couple_len = 0
        if len(seg) > 1:
            for prv, nxt in zip(seg, seg[1:]):
                sum_seg +=  self.compare(prv,nxt)
                couple_len += 1
            return float(sum_seg/couple_len)
        else:
            return 1.0

    ''' Calculate final similarity value of given individual '''
    def calculate_sim_of_individual(self, individual):
        sim = 0.0
        if len(individual) > 1:
            for i in individual:
                sim +=  self.calculate_cohesion(i)
            return float(sim/len(individual))
        else:
            return 1.0

    ''' Calculate similarity value between given two segments '''
    def calculate_simseg(self, segment1, segment2):
        divisor = len(segment1) * len(segment2)
        sum_sim = 0.0
        for x, y in [(x,y) for x in segment1 for y in segment2]:
            sum_sim += self.compare(x,y)
        return float(sum_sim/divisor)

    ''' Calculate final dissimilarity value of given individual '''
    def calculate_dissimilarity(self, segment_list):
        dissimilarity = 0.0
        compare_len = 0
        if len(segment_list) > 1:
            for prv, nxt in zip(segment_list, segment_list[1:]):
                dissimilarity += self.calculate_simseg(prv,nxt)
                compare_len += 1
            return float(1.0 -(dissimilarity/compare_len))
        else:
            return 0.0

    ''' Create similarity value list of given population
        returns a list that contains similarity values of individuals'''
    def create_similarity_value_list_of_population(self, ind_list):
        similarity = []
        for ind in ind_list:
            ind_sentences = self.get_segments_from_individual(ind,self.refined_sentences)
            sim = self.calculate_sim_of_individual(ind_sentences)
            similarity.append(sim)
        return similarity

    ''' Create dissimilarity value list of given population
        returns a list that contains dissimilarity values of individuals'''
    def create_dissimilarity_value_list_of_population(self, ind_list):
        dissimilarity = []
        for ind in ind_list:
            ind_sentences = self.get_segments_from_individual(ind,self.refined_sentences)
            dissim = self.calculate_dissimilarity(ind_sentences)
            dissimilarity.append(dissim)
        return dissimilarity

    ''' Create similarity and dissimilarity value list of given population
        returns a list that contains [similarity, dissimilarity] values of individuals'''
    def create_objective_value_list_of_population(self, ind_list):
        similarity = self.create_similarity_value_list_of_population(ind_list)
        dissimilarity = self.create_dissimilarity_value_list_of_population(ind_list)
        return [[item1,item2] for item1,item2 in zip(similarity, dissimilarity)]

    ''' Returns a list that contains non-dominated individual of given population
        and also this method uses pareto_frontier method'''
    def non_dominated(self, ind_list):
        result = []
        unique = self.remove_duplicate(ind_list)
        sim = self.create_similarity_value_list_of_population(unique)
        dis = self.create_dissimilarity_value_list_of_population(unique)
        temp = self.pareto_frontier(sim, dis, unique, maxX=True, maxY=True)
        for r in temp:
            result.append(r[2])
        return result

    ''' Apply pareto_frontier selection for maximization of both criteria
        and returns a list that contains pareto_frontier individuals of population'''
    def pareto_frontier(self, Xs, Ys, ind, maxX = True, maxY = True):
        myList = sorted([[Xs[i], Ys[i],ind[i]] for i in range(len(Xs))], reverse=maxX)
        p_front = [myList[0]]
        for pair in myList[1:]:
            if maxY:
                if pair[1] >= p_front[-1][1]:
                    p_front.append(pair)
            else:
                if pair[1] <= p_front[-1][1]:
                    p_front.append(pair)
        #p_frontX = [pair[0] for pair in p_front]
        #p_frontY = [pair[1] for pair in p_front]
        return p_front

    ''' Return a list that removed duplicate individuals
        used by non_dominated method '''
    def remove_duplicate(self, seq):
        if len(seq) > 1:
            seq.sort()
            last = seq[-1]
            for i in range(len(seq)-2, -1, -1):
                if last == seq[i]:
                    del seq[i]
                else:
                    last = seq[i]
            return seq
        else:
            return seq

    ''' Trial aggregation function it would be improved '''
    def calculate_aggregation(self, individual, alpha):
        sentence_repr = self.get_segments_from_individual(individual,self.refined_sentences)
        return self.calculate_sim_of_individual(sentence_repr)+(alpha*self.calculate_dissimilarity(sentence_repr))

    ''' Tuning fitness function'''
    def weightedValues(self, individual):
        v = [1]*(len(individual)+1)
        for i in xrange(len(individual)):
            if i == 0 :
                if individual[i] == 1:
                    v[i], v[i+1], v[i+2] = -numpy.log10(3),-numpy.log10(3),-numpy.log10(4)
            elif i == len(individual)-1:
                if individual[i] == 1:
                    v[i], v[i+1], v[i-1] = -numpy.log10(3),-numpy.log10(3),-numpy.log10(4)
            else:
                if individual[i] == 1:
                    v[i], v[i+1], v[i-1], v[i+2] = -numpy.log10(3),-numpy.log10(3),-numpy.log10(4),-numpy.log10(4)
        return v

    ''' Calculate internal cohesion value between segments
        used by calculate_sim_of_individual '''
    def calculate_weighted_cohesion(self, seg, weight):
        sum_seg = 0.0
        couple_len = 0
        if len(seg) > 1:
            for prv, nxt, w_prv, w_nxt in zip(seg, seg[1:], weight, weight[1:]):
                sum_seg +=  self.compare(prv,nxt)*(w_prv*w_nxt)
                couple_len += 1
            return float(sum_seg/couple_len)
        else:
            return 1.0

    ''' Calculate final similarity value of given individual '''
    def calculate_weighted_sim_of_individual(self, individual, weighted):
        sim = 0.0
        if len(individual) > 1:
            for i, j in zip(individual, weighted):
                sim +=  self.calculate_weighted_cohesion(i, j)
            return float(sim/len(individual))
        else:
            return 1.0

    ''' Calculate similarity value between given two segments '''
    def calculate_weighted_simseg(self, segment1, segment2, weight1, weight2):
        divisor = len(segment1) * len(segment2)
        sum_sim = 0.0
        for x, y, w_x, w_y  in zip(segment1, segment2, weight1, weight2):
            sum_sim += self.compare(x,y)*(w_x*w_y)
        return float(sum_sim/divisor)

    ''' Calculate final dissimilarity value of given individual '''
    def calculate_weighted_dissimilarity(self, segment_list, weight_list):
        dissimilarity = 0.0
        compare_len = 0
        if len(segment_list) > 1:
            for prv, nxt, w_prv, w_nxt in zip(segment_list, segment_list[1:], weight_list, weight_list[1:]):
                dissimilarity += self.calculate_weighted_simseg(prv, nxt, w_prv, w_nxt)
                compare_len += 1
            return float(1.0 -(dissimilarity/compare_len))
        else:
            return 0.0

    ''' Weighted value aggregation function, every sentence has a coefficient '''
    def calculate_weighted_aggregation(self, individual, alpha):
        weighted = self.weightedValues(individual)
        weighted_repr = self.get_segments_from_individual(individual, weighted)
        sentence_repr = self.get_segments_from_individual(individual, self.refined_sentences)
        return self.calculate_weighted_sim_of_individual(sentence_repr, weighted_repr)+(alpha*self.calculate_weighted_dissimilarity(sentence_repr, weighted_repr))

    ''' Weighted similarity list of population'''
    def weighted_similarity_value_list_of_population(self, ind_list):
        similarity = []
        for ind in ind_list:
            ind_sentences = self.get_segments_from_individual(ind,self.refined_sentences)
            weight = self.weightedValues(ind)
            weighted_repr = self.get_segments_from_individual(ind, weight)
            sim = self.calculate_weighted_sim_of_individual(ind_sentences,weighted_repr)
            similarity.append(sim)
        return similarity

    ''' Weighted dissimilarity list of population'''
    def weighted_dissimilarity_value_list_of_population(self, ind_list):
        dissimilarity = []
        for ind in ind_list:
            ind_sentences = self.get_segments_from_individual(ind,self.refined_sentences)
            weight = self.weightedValues(ind)
            weighted_repr = self.get_segments_from_individual(ind, weight)
            dissim = self.calculate_weighted_dissimilarity(ind_sentences,weighted_repr)
            dissimilarity.append(dissim)
        return dissimilarity

    ''' Weighted non-dominated'''
    def weighted_non_dominated(self, ind_list):
        result = []
        unique = self.remove_duplicate(ind_list)
        sim = self.weighted_similarity_value_list_of_population(unique)
        dis = self.weighted_dissimilarity_value_list_of_population(unique)
        temp = self.pareto_frontier(sim, dis, unique, maxX=True, maxY=True)
        for r in temp:
            result.append(r[2])
        return result


if __name__ == '__main__':
    print "Running Test..."


