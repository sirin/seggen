#! /usr/bin/env python
__author__ = 'sirin'

from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
from numpy import zeros,dot
from numpy.linalg import norm
from itertools import combinations
from datetime import datetime

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

    # used by compare method
    def doc_vec(self, doc, key_idx):
        v = zeros(len(key_idx))
        for word in doc:
            keydata = key_idx.get(word, None)
            if keydata:
                v[keydata[0]] = 1
        return v

    # used by calculate_cohesion method
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

    # used by calculate_sim_of_individual
    def calculate_cohesion(self, seg):
        sum_seg = 0.0
        couple_len = 0
        if len(seg) > 1:
            for prv, nxt in zip(seg, seg[1:]):
                sum_seg +=  self.compare(prv,nxt)
                couple_len += 1
            return sum_seg/couple_len
        else:
            return 1

    # used by compare_similarity method
    def calculate_sim_of_individual(self, individual):
        sim = 0.0
        if len(individual) > 1:
            for i in individual:
                sim +=  self.calculate_cohesion(i)
            return sim/len(individual)
        else:
            return 1

    # used by calculate_dissimilarity
    def calculate_simseg(self, segment1, segment2):
        divisor = len(segment1) * len(segment2)
        sum_sim = 0.0
        for x, y in [(x,y) for x in segment1 for y in segment2]:
            sum_sim += self.compare(x,y)
        return sum_sim / divisor

    # used by compare_dissimilarity
    def calculate_dissimilarity(self, segment_list):
        dissimilarity = 0.0
        compare_len = 0
        if len(segment_list) > 1:
            for prv, nxt in zip(segment_list, segment_list[1:]):
                dissimilarity += self.calculate_simseg(prv,nxt)
                compare_len += 1
            return (1.0 -(dissimilarity / compare_len))
        else:
            return 0 #TODO check this point and fix it!

    # used by non_dominated and dominates methods
    def compare_similarity(self, first, second):
        return self.calculate_sim_of_individual(first) >= self.calculate_sim_of_individual(second)

    # used by non_dominated and dominates methods
    def compare_dissimilarity(self, first, second):
        return self.calculate_dissimilarity(first) >= self.calculate_dissimilarity(second)

    def non_dominated(self, ind_list):
        result = []
        for combo in combinations(ind_list, 2):
            x_sentence = self.get_segments_from_individual(combo[0],self.refined_sentences)
            y_sentence = self.get_segments_from_individual(combo[1],self.refined_sentences)
            if self.compare_similarity(x_sentence,y_sentence) and self.compare_dissimilarity(x_sentence,y_sentence):
                result.append(combo[0])
        return self.remove_duplicate(result)

    # used by non_dominated method
    def remove_duplicate(self, seq):
        seq.sort()
        last = seq[-1]
        for i in range(len(seq)-2, -1, -1):
            if last == seq[i]:
                del seq[i]
            else:
                last = seq[i]
        return seq

    '''
    def dominates(self, x, y):
        x_sentence = self.get_segments_from_individual(x,self.refined_sentences)
        y_sentence = self.get_segments_from_individual(y,self.refined_sentences)
        return self.compare_similarity(x_sentence, y_sentence) and self.compare_dissimilarity(x_sentence, y_sentence)
    '''

    def calculate_aggregation(self, individual, alpha):
        sentence_repr = self.get_segments_from_individual(individual,self.refined_sentences)
        return self.calculate_sim_of_individual(sentence_repr)+(alpha*self.calculate_dissimilarity(sentence_repr))

    def create_similarity_value_list_of_population(self, ind_list):
        similarity = []
        for ind in ind_list:
            ind_sentences = self.get_segments_from_individual(ind,self.refined_sentences)
            sim = self.calculate_sim_of_individual(ind_sentences)
            similarity.append(sim)
        return similarity

    def create_dissimilarity_value_list_of_population(self, ind_list):
        dissimilarity = []
        for ind in ind_list:
            ind_sentences = self.get_segments_from_individual(ind,self.refined_sentences)
            dissim = self.calculate_dissimilarity(ind_sentences)
            dissimilarity.append(dissim)
        return dissimilarity

    def create_objective_value_list_of_population(self, ind_list):
        similarity = self.create_similarity_value_list_of_population(ind_list)
        dissimilarity = self.create_dissimilarity_value_list_of_population(ind_list)
        objective_list = [[item1,item2] for item1,item2 in zip(similarity,dissimilarity)]
        return objective_list


if __name__ == '__main__':
    print "Running Test..."
    util = Utility()
    lists = [[0,0,0,0,0,0,0,1,0,0,1,0,0],[0,0,0,0,0,1,0,0,0,0,1,0,0],[0,0,0,1,0,0,0,0,0,0,0,1,1],[0,0,0,1,0,0,0,1,0,0,0,1,0]]
    print util.non_dominated(lists)
    print util.running_times

