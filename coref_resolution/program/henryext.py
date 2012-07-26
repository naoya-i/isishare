#
# Henry external module for coreference experiment
#

import argparse
import sys, re, os, math

from collections import defaultdict

# "PRED(ARG1, ARG2, ARG3, ...)" => ("PRED", ["ARG1", "ARG2", "ARG3", ...])
def _break(lf):	lf = re.match( "(.*?)\((.*?)\)", lf ); return (lf.group(1), lf.group(2).split(","))

# You will find your file here.
def _myfile( x ):
	return os.path.join( g_mydir, x )

parser = argparse.ArgumentParser( description="An external module for coreference experiments.", prog="" )
parser.add_argument( "--argcons", help="Activate argument constraints.", action="store_true" )
parser.add_argument( "--condunif", help="Activate conditional unification constraints.", type=file, nargs="+" )
parser.add_argument( "--nedisj", help="Activate named entities disjointness constraints.", action="store_true" )
parser.add_argument( "--ineq", help="Activate explicit non-identity constraints.", type=file, nargs="+" )

if "argv" in dir(sys): parser.print_help(); sys.exit()

pa = parser.parse_args( _args )


#
# Have a welcome drink.
print >>sys.stderr, "Welcome to a discourse processing module!"

g_mydir		 = os.path.abspath(os.path.dirname(__file__))

#
g_boxer_nepreds		 = "per loc org nam ttl".split()
g_funcrel					 = defaultdict( list )
g_disj						 = {}
g_explicit_non_ids = []

#
# RESOURCE: CONDITIONAL UNIFICATION
g_cu =																																											 \
		re.findall( "set_condition\((.*?)'/", open( _myfile( "../data/cu-boxer.kb" ) ).read() ) +\
		re.findall( "set_condition\((.*?)'/", open( _myfile( "../data/cu-adj.kb" ) ).read() )

#
# RESOURCE: WORD FREQUENCY
g_word_freq	= dict( [(x.split()[1], int(x.split()[3])) for x in open( _myfile( "../data/entriesWithoutCollocates.txt" ) )] )

#
# RESOURCE: FUNCTIONAL RELATIONS
for ln in open( _myfile( "../data/func_relations-patterns.txt" ) ):
	ln, ln_broken = ln.strip().replace( "'", "" ), [_break(lit) for lit in ln.strip().replace( "'", "" ).split( " & " )]
	
	for lit in ln_broken:
		g_funcrel[ lit[0] ]	+= [(ln_broken, float(ln.split( "\t" )[1] if "\t" in ln else 0.0))]

#
# RESOURCE: INEQUALITIES
for ln in open( _myfile( "../data/inequality.kb" ) ):
	ret = re.findall( " ([^ ]+)'\((.*?)\)", ln.strip() )
	if 0 == len(ret): continue

	atoms	= [(x, y.split(",").index( "x" ) if "x" in y else -1, y.split(",").index( "y" ) if "y" in y else -1 ) for x, y in ret]
	mapper = defaultdict( list )

	# For isomorphic processing...
	if 1 == len(atoms): atoms += [atoms[0]]
	
	# Which arguments are expected to same?
	for predicate, args in ret:
		for i, arg in enumerate( args.split(",") ):
			mapper[ arg ] += [i]
	
	g_explicit_non_ids += [(atoms, dict( filter( lambda x: 1<len(x[1]), mapper.iteritems() ) ) )]
	
	
def _isExplicitNonIdent( p1p, p1a, p2p, p2a, ti, tip, tj, tjp ):
	
	for atoms, mapper in g_explicit_non_ids:

		if (atoms[0][0] == p1p and atoms[1][0] == p2p) or (atoms[0][0] == p2p and atoms[1][0] == p1p):

			if not ( (tip == atoms[0][1] and tjp == atoms[1][2]) or (tjp == atoms[0][1] and tip == atoms[1][2]) ): continue
			
			# Are the arguments same?
			for arg, pos in mapper.iteritems():
				if p1a.split(",")[ pos[0] ] != p2a.split(",")[ pos[1] ]: break
			else:
				return True

	return False


def _matchArgs( funcrel, p, a, v2h ):

	# Determine the first binding.
	binding = {}

	for pred, args in funcrel:
		if p == pred:
			for pos, arg in enumerate( a ):
				binding[ args[pos] ] = arg

	# Check the rest.
	# for pred, args in funcrel:
	# 	if p != pred:
	# 		for p in v2h.get( p, 
	# 	for pos, arg in enumerate( a ):
	# 		binding[ args[pos] ] = arg
					
	return binding


def _isEventArg( a, v2h ):
	for p in v2h.get( a, [] ):
		if "(%s," % a in p: return True
	return False


def _getNonFirstEventArg( pa, v2h ):
	for arg in pa.split(",")[1:]:
		if _isEventArg(arg, v2h): return arg


def _isProperNoun( a, v2h ):
	for p in v2h.get( a, [] ):
		if ",%s)" % a in p and p.split("(")[0] in g_boxer_nepreds: return True
	return False

#
# This is a callback function that decides how much two literals li
# and lj are evidential for the unification ti=tj.
#
# [Arguments]
#  ti, tj:         logical terms to be unified.
#  v2h:            mapping from logical terms to potential elemental hypotheses.
#
def cbGetUnificationEvidence( ti, tj, v2h, shallow_search=False ):

	# Different constants cannot be unified.
	if ti != tj and ti[0].isupper() and tj[0].isupper(): return []

	def _getArgPos( p, t ):
		return re.split( "[(,)]", p ).index(t) - 1

	if _isProperNoun(ti, v2h) and _isProperNoun(tj, v2h): return []
	
	ret = []
	
	for p1 in v2h.get( ti, [] ):
		p1l, p1id = p1.split( ":" )
		p1p, p1a	= p1l.split( "(" )
		p1a, p1id	= p1a[:-1], int(p1id)
		tip       = _getArgPos( p1l, ti )
		
		for p2 in v2h.get( tj, [] ):
			p2l, p2id = p2.split( ":" )
			p2p, p2a	= p2l.split( "(" )
			p2a, p2id	= p2a[:-1], int(p2id)
			tjp       = _getArgPos( p2l, tj )
			
			if ti != tj and _isExplicitNonIdent( p1p, p1a, p2p, p2a, ti, tip, tj, tjp ):
				
				# Ok, identifying coreference relation b/w ti and tj seems not good.
				ret += [(-10, "", [p1id, p2id])]
				continue
			
			#
			if p1id == p2id or (ti == tj and p1id > p2id): continue

			# Evidence provided by the same predicate
			if ti != tj and p1p == p2p and tip == tjp:
				
				# # Is this really evidence for coreference?
				if p1p in g_cu:           continue # Conditional unification predicates.
				if p1p.endswith( "-in" ): continue # Prepositional phrase.
				if p1p.endswith( "-rb" ): continue # Adverbs.

				# Is this functional predicates?
				if g_funcrel.has_key(p1p):
					for funcrel in g_funcrel[p1p]:
						args1, args2 = _matchArgs( funcrel[0], p1p, p1a.split(","), v2h ), _matchArgs( funcrel[0], p2p, p2a.split(","), v2h )
					
					# ret += [ (-1, "", [p1id, p2id, args1["y1"], args2["y1"]) ]
				
				# Are ti and tj non-first event arguments?
				if _isEventArg(ti, v2h) and _isEventArg(tj, v2h) and 0 != tip and 0 != tjp:
					continue

				# Is ti and tj the first event argument of proposition that have non-first event arguments?
				nfe1, nfe2 = _getNonFirstEventArg(p1l, v2h), _getNonFirstEventArg(p2l, v2h)

				if _isEventArg(ti, v2h) and _isEventArg(tj, v2h) and None != nfe1 and None != nfe2:

					# The evidence is provided by literals that have the non-first event arguments, instead of the occurrence of p1 and p2.
					if not shallow_search: ret += cbGetUnificationEvidence( nfe1, nfe2, v2h )
					
				 	continue
				
				# Otherwise, return how frequent the word is.
				ret += [ (1.0/math.log( g_word_freq.get( p1p, 2 ) ), p1p, [p1id, p2id]) ]

			# Disjoint?
			if g_disj.has_key("%s/1%s/1" % (p1p, p2p)) or g_disj.has_key("%s/1%s/1" % (p1p, p2p)):
				ret += [ (-9999, "", [p1id, p2id] ) ]

	#print ti, tj, ret
	
	return ret

