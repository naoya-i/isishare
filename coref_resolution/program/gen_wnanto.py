
from nltk import corpus

def _pr(s1, s2):
	if s1 > s2: s1, s2 = s2, s1
	print "%s\t%s" % ("%08d" % s1, "%08d" % s2)
	
for s in corpus.wordnet.all_synsets():
	for lemma in s.lemmas:
		for anto in lemma.antonyms():
			_pr(s.offset, anto.synset.offset)
