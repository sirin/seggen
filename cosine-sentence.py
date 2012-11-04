from nltk.tokenize import word_tokenize
from nltk import PorterStemmer
from numpy import zeros,dot
from numpy.linalg import norm 

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
    sumseg = 0
    couple_len = 0
    for prv, nxt in zip(seg, seg[1:]):
        sumseg +=  compare(prv,nxt)
        couple_len += 1
    return sumseg / couple_len

def fill_sentences_list(all_sentences,sentence):
    all_sentences.append(sentence)
    return all_sentences

def get_segments_from_individual(individual, sentences, segments):
    temp = []
    for i, j in zip(individual,range(len(sentences))):
        temp.append(sentences[j])
        if i == 1:
            #print j
            fill_sentences_list(segments,temp)
            #print temp
            temp = []
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


if __name__ == '__main__':
    print "Running Test..."
    #to automatize creating and appending docs
    test_sentences = []
    for i in open("/home/sirin/workspace/seggen/sample.txt"):
        fill_sentences_list(test_sentences,make_pre_steps(i))
    #there is a gap where converting sentences list to individual binary vector
    #it will be appended later
    #print calculate_cohesion(test_sentences)
    ind = [0,0,1]
    seg = []
    print get_segments_from_individual(ind,test_sentences,seg)
    l1 = ["I like to eat chicken noodle soup.","I have read the book Chicken noodle soup for the soul.","We like souls of booking not chicks."]
    l2 = ["Sometimes I want to eat noodle when read books."]
    print calculate_simseg(l1, l2)




