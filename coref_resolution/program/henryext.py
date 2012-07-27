#
# Henry external module for coreference experiment
#

from nltk import corpus

import argparse
import sys, re, os, math
import henryext

from collections import defaultdict

# "PRED(ARG1, ARG2, ARG3, ...)" => ("PRED", ["ARG1", "ARG2", "ARG3", ...])
def _break(lf):	lf = re.match( "(.*?)\((.*?)\)", lf ); return (lf.group(1), lf.group(2).split(","))

# You will find your file here.
def _myfile( x ):
	return os.path.join( g_mydir, x )

parser = argparse.ArgumentParser( description="An external module for coreference experiments.", prog="" )
parser.add_argument( "--argcons", help="Activate argument constraints.", action="store_true" )
parser.add_argument( "--condunif", help="Activate conditional unification constraints.", type=file, nargs="+" )
parser.add_argument( "--funcrel", help="Activate functional relations constraints.", type=file, nargs=1 )
parser.add_argument( "--waunif", help="Activate weighted unification.", type=file, nargs=1 )
parser.add_argument( "--ineq", help="Activate explicit non-identity constraints.", type=file, nargs=1 )
parser.add_argument( "--nedisj", help="Activate named entities disjointness constraints.", action="store_true" )
parser.add_argument( "--wndisj", help="Activate WordNet-based disjointness constraints.", action="store_true" )

if "argv" in dir(sys): parser.print_help(); sys.exit()

pa = parser.parse_args( _args.split() )


#
# Have a welcome drink.
print >>sys.stderr, "Welcome to a discourse processing module!"

g_mydir		 = os.path.abspath(os.path.dirname(__file__))

#
g_boxer_nepreds		 = "per loc org nam ttl".split()
g_funcrel					 = defaultdict( list )
g_disj						 = {}
g_explicit_non_ids = []

if pa.argcons: print >>sys.stderr, "Activated: ARGUMENT CONSTRAINTS"
if pa.wndisj:  print >>sys.stderr, "Activated: WORDNET DISJOINTNESS CONSTRAINTS"
if pa.nedisj:  print >>sys.stderr, "Activated: NAMED ENTITIES CONSTRAINTS"

#
# RESOURCE: CONDITIONAL UNIFICATION
g_cu = []

if None != pa.condunif:
	print >>sys.stderr, "Activated: CONDITIONAL UNIFICATION"
	
	for f in pa.condunif:
		g_cu += re.findall( "set_condition\((.*?)'/", f.read() )
	
#
# RESOURCE: WORD FREQUENCY
g_word_freq	= dict( [(x.split()[1], int(x.split()[3])) for x in pa.waunif[0]] ) if None != pa.waunif else {}

if 0 != len(g_word_freq):
	print >>sys.stderr, "Activated: WEIGHTED UNIFICATION"


#
# RESOURCE: FUNCTIONAL RELATIONS
g_funcrel = defaultdict( list )

if None != pa.funcrel:
	print >>sys.stderr, "Activated: FUNCTIONAL RELATIONS"
	
	for ln in pa.funcrel[0]:
		ln, ln_broken = ln.strip().replace( "'", "" ), [_break(lit) for lit in ln.strip().replace( "'", "" ).split( " & " ) ]
		
		for lit in ln_broken:
			g_funcrel[ lit[0] ]	+= [(ln_broken, float(ln.split( "\t" )[1] if "\t" in ln else 0.0))]

#
# RESOURCE: INEQUALITIES
g_explicit_non_ids = []

if None != pa.ineq:
	print >>sys.stderr, "Activated: EXPLICIT NON-IDENTITY"
	
	for ln in pa.ineq[0]:
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


def _getNounLiteral( t, v2h ):
	for p in v2h.get( t, [] ):
		if "-nn" in p and "%s)" % t in p: return p

		
def _isWNSibling( ti, tj, v2h ):
	pi, pj = _getNounLiteral(ti, v2h), _getNounLiteral(tj, v2h)

	if None == pi or None == pj: return False
	
	si, sj = corpus.wordnet.synsets( _break(pi)[0][:-3].replace( "-", "_" ) ), corpus.wordnet.synsets( _break(pj)[0][:-3].replace( "-", "_" ) )
		
	def _amIloved( x, y ):
		if x.name == y.name: return False
		
		for z in y.hypernyms():
			if not _amIloved( x, z ): return False

		return True

	if 0 < len(si) and 0 < len(sj):
		return _amIloved( sj[0], si[0] )

	return False


def _isSameWNSynset( ti, tj, v2h ):
	pi, pj = _getNounLiteral(ti, v2h), _getNounLiteral(tj, v2h)
	si, sj = corpus.wordnet.synsets( _break(pi)[0][:-3].replace( "-", "_" ) ), corpus.wordnet.synsets( _break(pj)[0][:-3].replace( "-", "_" ) )
	
	return False if 0 == len(si) or 0 == len(sj) else si[0].name == sj[0].name


# [P(x,y), Q(y,z)] => [(P(a,b), Q(b,c)), (P(d,e), Q(e,f)), ...]
def _getMatchingSets( query_literals ):
	eq = defaultdict( list )

	for i, lit in enumerate( query_literals ):
		for j, term in enumerate( lit[1] ):
			eq[term] += ["p%d.arg%d" % (1+i, j+1)]

	def _pairwise_eq(x):
		return " AND ".join( ["%s = %s" % (x[i], x[i+1]) for i in xrange(len(x)-1)] )
	
	query = "SELECT * FROM %s WHERE %s" % (
			", ".join( ["pehypothesis AS p%d" % (1+i) for i in xrange( len(query_literals) )] ),
			" AND ".join( ["p%d.predicate = '%s'" % (1+i, query_literals[i][0]) for i in xrange( len(query_literals) )] + [_pairwise_eq(x) for x in eq.values() if 1 < len(x)] ) )
	#print >>sys.stderr, query
	
	eq	 = defaultdict(set)
	inst = henryext.getPotentialElementalHypotheses( query )
	
	for literals in inst:
		
		for i, lit in enumerate( query_literals ):
			for j, term in enumerate( lit[1] ):
				eq[ query_literals[i][1][j] ] |= set( [literals[ i*8 + 2+j ]] )
				
	return (eq, inst)

#
# This is a callback function that decides how much two literals li
# and lj are evidential for the unification ti=tj.
#
# [Arguments]
#  ti, tj:         logical terms to be unified.
#  v2h:            mapping from logical terms to potential elemental hypotheses.
#
def cbGetUnificationEvidence( ti, tj, v2h, shallow_search=False ):
	
	#print henryext.getPotentialElementalHypotheses
	
	# Different constants cannot be unified.
	if ti != tj and ti[0].isupper() and tj[0].isupper(): return []

	def _getArgPos( p, t ):
		return re.split( "[(,)]", p ).index(t) - 1

	if pa.nedisj and ti != tj and _isProperNoun(ti, v2h) and _isProperNoun(tj, v2h) and not _isSameWNSynset(ti, tj, v2h):
		return [ (-10.0, "", [ int(_getNounLiteral(ti, v2h).split(":")[1]), int(_getNounLiteral(tj, v2h).split(":")[1]) ]) ]
	
	if pa.wndisj and ti != tj and _isWNSibling(ti, tj, v2h):
		return [ (-10.0, "", [ int(_getNounLiteral(ti, v2h).split(":")[1]), int(_getNounLiteral(tj, v2h).split(":")[1]) ]) ]
	
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

				# Is this functional predicates (excluding prepositions for reducing search space)?
				if "-in" not in p1p and g_funcrel.has_key(p1p):
					for funcrel, score in g_funcrel[p1p]:

						subs, insts = _getMatchingSets(funcrel)

						if 0 < len(subs):
							print >>sys.stderr, "Hit functional relation:", funcrel, insts, subs
							print >>sys.stderr, subs["x1"], subs["x2"]
							
							if 1 < len(subs["x2"]):
								print >>sys.stderr, subs["x1"], "should be different."

								if ti in subs["x1"] and tj in subs["x1"]:
									ret += [(-9999, "", [p1id, p2id])]
							
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
				ret += [ (-1.0/math.log( g_word_freq.get( p1p, 2 ) )*0.01, p1p, [p1id, p2id]) ]

			# Disjoint?
			if g_disj.has_key("%s/1%s/1" % (p1p, p2p)) or g_disj.has_key("%s/1%s/1" % (p1p, p2p)):
				ret += [ (-9999, "", [p1id, p2id] ) ]

		
	#print ti, tj, ret
	
	return ret

