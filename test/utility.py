from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
from numpy import zeros,dot
from numpy.linalg import norm
from itertools import combinations

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

def clear_stopwords(words, stopwords):
    for stopword in stopwords:
        words = filter(lambda x:x!=stopword, words)
    return words

def add_word(all_words, word):
    all_words.setdefault(word,0)
    all_words[word] += 1

def doc_vec(doc,key_idx):
    v=zeros(len(key_idx))
    for word in doc:
        keydata=key_idx.get(word, None)
        if keydata:
            v[keydata[0]] = 1
    return v

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
    for i in open("/home/sirin/workspace/seggen/stopwords.txt"):
        stopwords.append(i.replace("\n",""))
    text = replace_all(text, replacement_chars)
    words = word_tokenize(text)
    words = [word.lower() for word in words]
    words = clear_stopwords(words, stopwords)
    words = [porter.stem(word) for word in words]
    return words

def compare(doc1,doc2):
    all_words=dict()
    for w in doc1:
        add_word(all_words,w)
    for w in doc2:
        add_word(all_words,w)
    key_idx=dict() # key-> ( position, count )
    keys=all_words.keys()
    keys.sort()
    for i in range(len(keys)):
        key_idx[keys[i]] = (i,all_words[keys[i]])
    del keys
    del all_words

    v1=doc_vec(doc1,key_idx)
    v2=doc_vec(doc2,key_idx)
    return float(dot(v1,v2) / (norm(v1) * norm(v2)))

def calculate_cohesion(seg):
    sumseg = 0.0
    couple_len = 0
    if len(seg) > 1:
        for prv, nxt in zip(seg, seg[1:]):
            sumseg +=  compare(prv,nxt)
            couple_len += 1
        return sumseg / couple_len
    else:
        return 1

def calculate_sim_of_individual(individual):
    sim = 0.0
    if len(individual) > 1:
        for i in individual:
            sim +=  calculate_cohesion(i)
        return sim
    else:
        return 1

def fill_sentences_list(all_sentences,sentence):
    all_sentences.append(sentence)
    return all_sentences

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

def calculate_simseg(segment1, segment2):
    divisor = len(segment1) * len(segment2)
    sumsim = 0.0
    for x, y in [(x,y) for x in segment1 for y in segment2]:
        sumsim += compare(x,y)
    return sumsim / divisor

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

#calculating hardness value part is missing!
#think about to implement this function in a class(other file)
def select_nondominated(ind_list):
    return "hello"

def non_dominated(mylist):
    temp = []
    for combo in combinations(mylist, 2):
        temp.append(combo)
    return temp

if __name__ == '__main__':
    print "Running Test..."
    #to automatize creating and appending docs
    test_sentences = []
    for i in open("/home/sirin/workspace/seggen/sample.txt"):
        fill_sentences_list(test_sentences,make_pre_steps(i))
    #there is a gap where converting sentences list to individual binary vector
    #it will be appended later
    print 'Test sentences are: %s' % test_sentences
    ind_list = []
    ind = [0,0,1]
    print 'Individual vector is: %s' % ind
    segment_list = []
    segment_list = get_segments_from_individual(ind,test_sentences)
    ind_list.append(segment_list)
    ind2 = [1,0,0]
    print 'Individual vector-2 is: %s' % ind2
    segment_list2 = []
    segment_list2 = get_segments_from_individual(ind2,test_sentences)
    ind_list.append(segment_list2)
    ind3 = [0,1,0]
    print 'Individual vector-3 is: %s' % ind3
    segment_list3 = []
    segment_list3 = get_segments_from_individual(ind3,test_sentences)
    ind_list.append(segment_list3)

    print 'Segment list for individual vector: %s' % segment_list
    print 'Similarity for individual vector: %s' % calculate_sim_of_individual(segment_list)
    for i in segment_list:
        print 'Internal cohesion of each segment is: %s' % calculate_cohesion(i)
    print 'Dissimilarity of adjacent segments is: %s' % calculate_dissimilarity(segment_list)
    print 'Select non-dominated result is: %s' % select_nondominated(ind_list)



