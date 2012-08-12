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
# Please have a welcome drink.
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
g_funcrel_list = []
g_funcrel			 = defaultdict( list )

if None != pa.funcrel:
	print >>sys.stderr, "Activated: FUNCTIONAL RELATIONS"

	g_funcrel_list = [(ln.split("\t")[0], (1/6406.84)*float(ln.split("\t")[1])) for ln in pa.funcrel[0] if 2 == len(ln.split("\t"))]
	
	for ln in pa.funcrel[0]:
		ln, ln_broken = ln.strip().replace( "'", "" ), [_break(lit) for lit in ln.strip().replace( "'", "" ).split( " & " ) ]
		
		for lit in ln_broken:
			g_funcrel[ lit[0] ]	+= [(ln_broken, float(ln.split( "\t" )[1] if "\t" in ln else 0.0))]

#
# RESOURCE: INEQUALITIES
g_explnids_list = []
g_explicit_non_ids = []

if None != pa.ineq:
	print >>sys.stderr, "Activated: EXPLICIT NON-IDENTITY"

	g_explnids_list = [ln.split( "x!=y => " )[1] for ln in pa.ineq[0] if 2 == len( ln.split( "x!=y => " ) )]
	
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
				eq[ query_literals[i][1][j] ] |= set( [literals[ i*(MaxBasicProp+MaxArguments) + MaxBasicProp+j ]] )

	eq = dict( [(x, list(y)) for x, y in eq.iteritems()] )
	
	return (eq, inst)


def sfFnUnify( args ):
	fn1, fn2, coref = args
	if int(fn1[0]) >= int(fn2[0]): return []
	if fn1[0] in fn2[2].split() or fn2[0] in fn1[2].split(): return []
	if 0 < len(set(fn1[2].split()) & set(fn2[2].split())): return []
	if coref[MaxBasicProp+0] == coref[MaxBasicProp+1]: return []
	if coref[MaxBasicProp+0].startswith("_") and coref[MaxBasicProp+1].startswith("_"): return []

	# Argpos???
	
	return [ ("FN_%s" % fn1[1], 1) ]

	
def sfRelUnify( args ):
	ls1, ls2, lcs, lcoref1, lcoref2 = args
	if int(ls1[0]) >= int(ls2[0]): return []
	
	if lcoref1[MaxBasicProp+0] == lcoref1[MaxBasicProp+1]: return []
	if lcoref2[MaxBasicProp+0] == lcoref2[MaxBasicProp+1]: return []
	if 0 < len(set(ls1[2].split()) & set(ls2[2].split())): return []

	#print >>sys.stderr, ls1
	
	return [("REL_%s" % lcs[1], 1)]


def sfBaseCorefProp( args ):

	# Named entities
	n1, n2 = args[0][1], args[1][1]
	ret = []

	if int(args[0][0]) >= int(args[1][0]): return []
	
	s1 = corpus.wordnet.synsets( "_".join( n1.split("-")[:-1] ) )
	s2 = corpus.wordnet.synsets( "_".join( n2.split("-")[:-1] ) )

	#ret += [("PROPER_NAME_" % , 1)]
	#if args[2].split()[1] == args[3].split()[1]: ret += [("PN_SEMCLASS_" + args[2].split()[1], 1)]
	#if args[2].split()[1] == args[3].split()[1]: ret += [("PN_COMMON_STR", 1)]

	# if 0 < len( set([x.name for x in s1]) & set([x.name for x in s2]) ): ret += [("PNS_WN_CLASS", 1)]
	# else:                                                                ret += [("PNS_WN_NOT_CLASS", 1)]
	
	return ret


def sfBaseCoref( args ):
	v1, v2 = args[2][MaxBasicProp+0], args[2][MaxBasicProp+1]
	n1, n2 = args[0][1], args[1][1]
	ret = []

	if int(args[0][0]) >= int(args[1][0]): return []
	if v1 == v2: return []

	#if "-vb" in n1: ret += [("VB_%d" % args[0].index(v1), 1)]
	
	if n1 == n2: ret += [("STR_COMP_MATCH_%s" % n1, 1)]
	
	for pm in set( n1.split("-")[:-1] ) & set( n2.split("-")[:-1]):
		ret += [("STR_PARTIAL_MATCH_%s" % pm, 1)]

	# ret += [("STR_BAG_MATCH_%s" % "".join(set(n1)&set(n2)), 1)]

	s1 = corpus.wordnet.synsets( "_".join( n1.split("-")[:-1] ) )
	s2 = corpus.wordnet.synsets( "_".join( n2.split("-")[:-1] ) )

	adj1 = henryext.getPotentialElementalHypotheses( "SELECT * FROM pehypothesis as p WHERE p.predicate LIKE '%-%adj' AND p.arg2 = '%s'" % v1 ) if 0 == len(s1) else []
	adj2 = henryext.getPotentialElementalHypotheses( "SELECT * FROM pehypothesis as p WHERE p.predicate LIKE '%-%adj' AND p.arg2 = '%s'" % v2 ) if 0 == len(s2) else []

	if n2.startswith( "~" ):
		if 0 < len(adj1) and 0 == len(s1): s1 = corpus.wordnet.synsets( adj1[0][1].split( "-adj" )[0] )
			
		# ret += [("PRONOUN", 1)]
		# ret += [("PRN_DIST_%d" % min(2,abs(int(v1.split("x")[0]) - int(v2.split("x")[0]))/2), 1)]

		#print >>sys.stderr, n1, v1, v2, n2

		if abs(int(v1.split("x")[0]) - int(v2.split("x")[0])) > 2:
			ret += [("PRN_VERY_FAR", 1)]
		
		if int(v1.split("x")[0]) > int(v2.split("x")[0]):
			ret += [("PRN_POS_-1", 1)]
		
		for s in s1:
			ret += [("PRN_%s,%s" % (n2, s), 1)]

	# else:
	# 	ret += [("DIST_%d" % min(2,abs(int(v1.split("x")[0]) - int(v2.split("x")[0]))/2), 1)]
		
	# print "_".join( n1.split("-")[:-1]), s1
	# print "_".join( n2.split("-")[:-1]), s2

	if 0 < len(adj1) and 0 == len(s1): s1 = corpus.wordnet.synsets( adj1[0][1].split( "-adj" )[0] )
	if 0 < len(adj2) and 0 == len(s2): s2 = corpus.wordnet.synsets( adj2[0][1].split( "-adj" )[0] )
		
	if 0 < len(s1) and 0 < len(s2):

		for st1 in s1:
			for st2 in s2:
				for ch in set([x.name for x in st1.hypernyms()]) & set([x.name for x in st2.hypernyms()]):
					ret += [("WN_COMMON_HYPERNYM_%s" % ch, 1)]
				
		for cls in set([x.name for x in s1]) & set([x.name for x in s2]):
			ret += [("WN_COMMON_CLASS_%s" % cls, 1)]
		
		# for p in s1[0].hypernym_paths():
		# 	if s2[0].name in set([x.name for x in p]): ret += [("WN_PATH_%s" % s1[0], 1)]; break

		# else:
		# 	for p in s2[0].hypernym_paths():
		# 		if s1[0].name in set([x.name for x in p]): ret += [("WN_PATH_%s" % s2[0], 1)]; break
		# 	else:

		# 		# WordNet disjointness
		# 		pass #ret += [("WN_NOPATH", 1)]

		# Antonym
		if 0 < len( set([x.synset.name for x in s1[0].lemmas[0].antonyms()]) & set([x.synset.name for x in s2[0].lemmas[0].antonyms()]) ):
			ret += [("WN_ANTONYM", 1)]
	
	return ret


def cbScoreFunction():

	ret = []
	
	# Functional Words
	for lfs, score in g_funcrel_list:
		eq, inst = _getMatchingSets( [_break(lf.replace( "'", "" )) for lf in lfs.split( " & " )] )
		
		if 2 == len(inst) and 2 <= len(eq["x2"]): ret += ["((\"FUNC_REL_%s\" %f) (^ (= %s %s) ) )" % ("".join(["".join(x) for x in inst[1]]), score, eq["x1"][0], eq["x1"][1]) ]

	# Explicit Non-identity
	for lfs in g_explnids_list:
		eq, inst = _getMatchingSets( [_break(lf.replace( "'", "" )) for lf in lfs.split( " & " )] )

		if 0 < len(eq) and "" != eq["x"][0] and "" != eq["y"][0]: ret += ["((EXPL_NID 1) (^ (= %s %s) ) )" % (eq["x"][0], eq["y"][0])]
	
	# Argument Constraints
	
		
	return "\n".join(ret)


#
# Loss function
#
def cbGetLoss( system, gold ):
	
	# Check the coreference outputs
	system_eq		= [_break(lf) for lf in system.split( " ^ " ) if lf.startswith("=")]
	system_ineq	= [_break(lf) for lf in system.split( " ^ " ) if lf.startswith("!=")]
	gold_eq			= [_break(lf) for lf in gold.split( " ^ " ) if lf.startswith("=")]

	num_max_score = 0
	num_score			= 0

	# Shrink the cluster
	num_inc_cluster = True
	
	while num_inc_cluster:
		ncls						= {}
		idx							= {}
		n								= 0
		num_inc_cluster = False

		for c in gold_eq:
			for t in c[1]:
				if idx.has_key(t):
					ncls[ idx[t] ] += c[1]
					num_inc_cluster = True
					break
			else:
				ncls[n] = c[1]

				for t in c[1]:
					idx[t] = n

				n+= 1
				
		gold_eq = [("=", x) for x in ncls.values()]
				
	
	for cluster in system_eq:
		for i, ti in enumerate( cluster[1] ):
			if ti.startswith( "_" ): continue
			
			for tj in cluster[1][i+1:]:
				if tj.startswith( "_" ): continue
				num_max_score += 1

				for gcluster in gold_eq:
					if ti in gcluster[1] and tj in gcluster[1]: num_score += 1; break
				else:
					print ti, tj, "should not be unified."

	for cluster in system_ineq:
		for i, ti in enumerate( cluster[1] ):
			if ti.startswith( "_" ): continue
			
			for tj in cluster[1][i+1:]:
				if tj.startswith( "_" ): continue
				num_max_score += 1
				
				for gcluster in gold_eq:
					if ti in gcluster[1] and tj in gcluster[1]: print ti, tj, "should be unified."; break
				else:
					num_score += 1; 

	print "Score:", num_score, "/", num_max_score

	if 0 == num_max_score: return 0
	
	return (1.0 - (1.0 * num_score / num_max_score))


	if pa.nedisj and ti != tj and _isProperNoun(ti, v2h) and _isProperNoun(tj, v2h) and not _isSameWNSynset(ti, tj, v2h):
		return [ (-10.0, "", [ int(_getNounLiteral(ti, v2h).split(":")[1]), int(_getNounLiteral(tj, v2h).split(":")[1]) ]) ]
	
	if pa.wndisj and ti != tj and _isWNSibling(ti, tj, v2h):
		return [ (-10.0, "", [ int(_getNounLiteral(ti, v2h).split(":")[1]), int(_getNounLiteral(tj, v2h).split(":")[1]) ]) ]
	
	ret = []
	
			# 	# # Is this really evidence for coreference?
			# 	if p1p in g_cu:           continue # Conditional unification predicates.
			# 	if p1p.endswith( "-in" ): continue # Prepositional phrase.
			# 	if p1p.endswith( "-rb" ): continue # Adverbs.

			# 	# Are ti and tj non-first event arguments?
			# 	if _isEventArg(ti, v2h) and _isEventArg(tj, v2h) and 0 != tip and 0 != tjp:
			# 		continue

			# 	# Is ti and tj the first event argument of proposition that have non-first event arguments?
			# 	nfe1, nfe2 = _getNonFirstEventArg(p1l, v2h), _getNonFirstEventArg(p2l, v2h)

			# 	if _isEventArg(ti, v2h) and _isEventArg(tj, v2h) and None != nfe1 and None != nfe2:

			# 		# The evidence is provided by literals that have the non-first event arguments, instead of the occurrence of p1 and p2.
			# 		if not shallow_search: ret += cbGetUnificationEvidence( nfe1, nfe2, v2h )
					
			# 	 	continue
				
			# 	# Otherwise, return how frequent the word is.
			# 	ret += [ (-1.0/math.log( g_word_freq.get( p1p, 2 ) )*0.01, p1p, [p1id, p2id]) ]

