#
# Henry extension module for coreference experiment
#

import sys, re, os, math

from lxml import etree
from collections import defaultdict

def _myfile( x ):
	return os.path.join( g_mydir, x )

g_mydir		 = os.path.abspath(os.path.dirname(__file__))

g_cu        = \
		re.findall( "set_condition\((.*?)'/", open( _myfile( "../data/cu-boxer.kb" ) ).read() ) + \
		re.findall( "set_condition\((.*?)'/", open( _myfile( "../data/cu-adj.kb" ) ).read() )
g_word_freq = dict( [(x.split()[1], int(x.split()[3])) for x in open( _myfile( "../data/entriesWithoutCollocates.txt" ) )] )
g_disj = {}

#
# This is a callback function that decides how much two literals li
# and lj are evidential for the unification ti=tj.
#
# [Arguments]
#  ti, tj:         logical terms to be unified.
#  v2h:            mapping from logical terms to potential elemental hypotheses.
#
def cbGetUnificationEvidence( ti, tj, v2h ):

	# Different constants cannot be unified.
	if ti != tj and ti[0].isupper() and tj[0].isupper(): return []
		
	def _getArgPos( p, t ):
		return re.split( "[(,)]", p ).index(t) - 1
	
	ret = []
	
	for p1 in v2h.get( ti, [] ):
		p1	 = p1.split( ":" )
		p1id = int(p1[-1])
		
		for p2 in v2h.get( tj, [] ):
			p2	 = p2.split( ":" )
			p2id = int(p2[-1])
			
			#
			if p1id == p2id or (ti == tj and p1id > p2id): continue
			
			# Evidence provided by the same predicate
			if ti != tj and _getArgPos( p1[0], ti ) == _getArgPos( p2[0], tj ) and p1[0].split("(")[0] == p2[0].split("(")[0]:
				
				# # Is this really evidence for coreference?
				if p1[0].split("(")[0] in g_cu:           continue # Conditional unification predicates.
				if p1[0].split("(")[0].endswith( "-in" ): continue # Prepositional phrase.
				if p1[0].split("(")[0].endswith( "-rb" ): continue # Adverbs.

				# Otherwise, return how frequent the word is.
				ret += [ (-0.1*math.log( g_word_freq.get( p1[0].split("-")[0], 2 ) ), [p1id, p2id]) ]

			# # Disjoint?
			if g_disj.has_key("%s/1%s/1" % (p1[0].split("(")[0], p2[0].split("(")[0])) or g_disj.has_key("%s/1%s/1" % (p1[0].split("(")[0], p2[0].split("(")[0])):
				ret += [ (-9999, [p1id, p2id] ) ]

	return ret

