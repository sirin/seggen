from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
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
	lemmatizer = WordNetLemmatizer()
	porter = PorterStemmer()
	for i in open("/home/sirin/Desktop/seggen/stopwords.txt"):
		stopwords.append(i.replace("\r\n",""))
	text = replace_all(text, replacement_chars)
	words = word_tokenize(text)
	words = [word.lower() for word in words]
	words = clear_stopwords(words, stopwords)
	words = [lemmatizer.lemmatize(word) for word in words]
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

if __name__ == '__main__':
 print "Running Test..." 
 doc1=make_pre_steps("I like to eat chicken noodle soup.")
 doc2=make_pre_steps("I have read the book Chicken noodle soup for the soul.")
 print "Using Doc1: %s\n\nUsing Doc2: %s\n" % ( doc1, doc2 )
 print "Similarity %s" % compare(doc1,doc2)



