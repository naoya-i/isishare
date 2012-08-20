#
# Henry external module for coreference experiment
#

from nltk import corpus

import cdb

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
parser.add_argument( "--ineq", help="Activate explicit non-identity constraints.", type=file, nargs=1 )
parser.add_argument( "--nedisj", help="Activate named entities disjointness constraints.", action="store_true" )
parser.add_argument( "--wndisj", help="Activate WordNet-based disjointness constraints.", action="store_true" )
parser.add_argument( "--wnannotate", help="Annotate synset predicates in preprocessing.", action="store_true" )
parser.add_argument( "--caching", help="Create caches.", default="" )

pa = parser.parse_args( sys.argv[1:] if "argv" in dir(sys) else _args.split() )

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
# RESOURCE: FRAMENET SELECTIONAL RESTRICTION
g_fnsr = {}

print >>sys.stderr, "Loading FrameNet selectional restriction..."

for ln in open(_myfile("../data/fn-sr.lisp")):
	ln = re.findall( "\(=> \((.*?) s x :([0-9.]+)\) \((FN[^ ]+) (.*?)\)", ln )

	if 1 == len(ln):
		g_fnsr["%s-%s" % (ln[0][0], ln[0][2])] = (ln[0][0], float(ln[0][1]), ln[0][2], ln[0][3].split())
	

#
# RESOURCE: SCHEMA
print >>sys.stderr, "Loading schema..."

g_schema = {}

if os.path.exists( "/work/naoya-i/conll-2012/schemas-size12.cdb" ):
	print >>sys.stderr, "Using cache!"
	g_schema = cdb.init( "/work/naoya-i/conll-2012/schemas-size12.cdb" )
	
else:
	if "schema" in pa.caching: maker = cdb.cdbmake( _myfile("../data/schemas-size12.cdb"), _myfile("../data/schemas-size12.cdb.tmp") )

	schema_id = 0
	
	for score, events, event_scores, roles in re.findall( "\*\*\*\*\*\nscore=([-0-9.]+)\nEvents: (.*?)\nScores: (.*?)\n(.*?)\n\n", open( _myfile("../data/schemas-size12") ).read(), re.MULTILINE|re.DOTALL ):

		schema_id += 1
		scores_dict = {}

		for i, e in enumerate(events.split()):
			scores_dict[e] = float(event_scores.split()[i])

		role_id = 0
		
		for verbs, rolefillers in re.findall( "\[ (.*?) \] \( (.*?)\)", roles ):
			role_id += 1
			
			for e in verbs.split( " " ):
				if "schema" in pa.caching: maker.add( e, "%d-%d,%s,%f" % (schema_id, role_id, events, 0) )
				
				for filler, filler_score in re.findall( "([^ ]+) ([0-9.-]+)", rolefillers ):
					if "schema" in pa.caching: maker.add( "%s,%s" % (e, filler), "%d-%d,%s,%f" % (schema_id, role_id, events, float(filler_score) + scores_dict[e[:-2]]) )

	if "schema" in pa.caching: maker.finish()
		

#
# RESOURCE: CONDITIONAL UNIFICATION
print >>sys.stderr, "Loading conditional unification files..."
g_cu = []

if None != pa.condunif:
	print >>sys.stderr, "Activated: CONDITIONAL UNIFICATION"
	
	for f in pa.condunif:
		g_cu += re.findall( "set_condition\((.*?)'/", f.read() )
	
#g_word_freq	= dict( [(x.split()[1], int(x.split()[3])) for x in _myfile("./data/WN_abstraction_level.txt")] ) if None != _myfile("./data/WN_abstraction_level.txt") else {}
#g_word_abst = dict( [(x.split()[0], int(x.split()[3])) for x in _myfile("./data/WN_abstraction_level.txt")] )

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
	

		
if "argv" in dir(sys): parser.print_help(); sys.exit()

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
def _getMatchingSets( ctx, query_literals ):
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
	inst = henryext.getPotentialElementalHypotheses( ctx, query )
	
	for literals in inst:
		
		for i, lit in enumerate( query_literals ):
			for j, term in enumerate( lit[1] ):
				eq[ query_literals[i][1][j] ] |= set( [literals[ i*(MaxBasicProp+MaxArguments) + MaxBasicProp+j ]] )

	eq = dict( [(x, list(y)) for x, y in eq.iteritems()] )
	
	return (eq, inst)


def cbScoreFunctionPairwiseFilter():

	for i in xrange(383):
		for j in xrange(383):
			print "wao"
		
	return [
		("FrameNet",   1, "^FN", "^FN"),
		("FrameNetSR", 0, "^FN", "^synset1"),
		("WNSynset",   1, "^synset", "^synset"),
		("NPCoref",    0, "-nn$", "-nn$"),
		("PrnCoref",   0, "-nn$", "^~")
		]


def test():
	return

def cbScoreFunctionElement( ctx, p ):
	return ([], [("HYPOTHESIZED", 0)])


def cbScoreFunctionFrameNet( ctx, fn1, fn2 ):
	return ( [(fn1[1][i], fn2[1][i]) for i in xrange(len(fn1[1])) if fn1[1][i][0] != "_" and fn2[1][i][0] != "_"], [("FN_UNIFY", 1)] )


def cbScoreFunctionFrameNetSR( ctx, fn, syn ):
	fnsr = g_fnsr.get( "%s-%s" % (syn[0], fn[0]) )
	if None == fnsr: return ()

	return ( [(fn[1][fnsr[3].index("x")], syn[1][1])], [("FN_SEL_RESTR_Y", -1+fnsr[1])] )


def cbScoreFunctionWNSynset( ctx, p, q ):
	return ( [(p[1][1], q[1][1])], [("WN_COMMON_SYNSET_Y", 1)] )


def cbScoreFunctionNPCoref( ctx, p, q ):
	v1, v2 = p[1][1], q[1][1]
	n1, n2 = p[0],    q[0]
	
	if v1 == v2: return ()

	ret = {}

	# COMMON PROPERTY FEATURE
	for vb1, vbargs1, vbid1 in henryext.getLiteralsFromTerm( ctx, v1 ):
		if vb1.startswith( "synset" ): continue
		
		for vb2, vbargs2, vbid2 in henryext.getLiteralsFromTerm( ctx, v2 ):
			if vb2.startswith( "synset" ): continue

			vb1suff, vb2suff = vb1.split("-")[-1], vb2.split("-")[-1]

			if vbid1 == vbid2 and vb1 not in ["="]:
				ret["ARGS_OF_SAME_PREDS"] = ("Y", -1)
			
			if vb1suff in ["vb", "adj", "in"] and vb2.split("-")[-1] in ["vb", "adj", "in"] and vbargs1.index(v1) == vbargs2.index(v2):
				if "in" == vb1suff and "in" == vb2suff and vbargs1[1] == v1 and vbargs2[1] == v2 and 3 == len(vbargs1) and 3 == len(vbargs2):

					for vbin1, vbinargs1, vbinid1 in henryext.getLiteralsFromTerm( ctx, vbargs1[2] ):
						for vbin2, vbinargs2, vbinid2 in henryext.getLiteralsFromTerm( ctx, vbargs2[2] ):
							if not (vbin1.endswith( "-nn" ) and vbin2.endswith( "-nn" )): continue
							if vbin1 == vbin2: ret["CP_PREP_STR_MATCH"] = ("Y", 1)
							else:
								vbin1syn, vbin2syn = corpus.wordnet.synsets(vbin1.split("-")[-2]), corpus.wordnet.synsets(vbin2.split("-")[-2])

								if 0 < len(vbin1syn) and 0 < len(vbin2syn):
									if 0 < len(set(vbin1syn) & set(vbin2syn)): ret[ "CP_PREP_WN_COMMON_SYNSET" ] = ("Y", 1)
								
				if "vb" == vb1suff and "vb" == vb2suff:
					if vb1 == vb2: ret["CP_EVENT_FILLER_STR_MATCH"] = ("Y", 1)
					else:
						vb1syn, vb2syn = corpus.wordnet.synsets(vb1.split("-")[-2]), corpus.wordnet.synsets(vb2.split("-")[-2])

						if 0 < len(vb1syn) and 0 < len(vb2syn):
							if 0 < len(set(vb1syn) & set(vb2syn)): ret[ "CP_EVENT_FILLER_WN_COMMON_SYNSET" ] = ("Y", 1)
					
				if "adj" == vb1suff and "adj" == vb2suff:
					if vb1 == vb2: ret["CP_ADJ_STR_MATCH"]          = ("Y", 1)
					else:
						vb1syn, vb2syn = corpus.wordnet.synsets(vb1.split("-")[-2]), corpus.wordnet.synsets(vb2.split("-")[-2])

						if 0 < len(vb1syn) and 0 < len(vb2syn):
							if 0 < len(set(vb1syn) & set(vb2syn)): ret[ "CP_ADJ_WN_COMMON_SYNSET" ] = ("Y", 1)
					
	
	# SURFACE MATCH FEATURE.
	if n1 == n2: ret["CP_NOUN_STR_MATCH"] = ("COMP", 1)
	else:
		for pm in set( n1.split("-")[:-1] ) & set( n2.split("-")[:-1]):
			ret["CP_NOUN_STR_MATCH"] = ("HEAD", 1); break
		# else:
		# 	ret["CP_NOUN_STR_MATCH"] = ("NO_MATCH", -1)

	# DISTANCE.
	# try:
	# 	ret[ "NP-NP_SENTDIST" ] = ("%d" % min(1,abs(int(v1.split("x")[0]) - int(v2.split("x")[0]))), 1)
	# except ValueError:
	# 	pass

	# WORDNET FEATURES.
	s1 = corpus.wordnet.synsets( "_".join( n1.split("-")[:-1] ) )
	s2 = corpus.wordnet.synsets( "_".join( n2.split("-")[:-1] ) )

	if 0 < len(s1) and 0 < len(s2):
		ret.update({
				#"WN_COMMON_SYNSET": ("N", -1),
				#"WN_ON_PATH":       ("N", -1),
				#"WN_SIBLING":       ("N", 1),
				#"WN_ANTONYM":       ("N", 1),
				})

		st1, st2 = s1[0], s2[0]

		# for st1 in s1:
		# 	for st2 in s2:
		hp1, hp2 = st1.hypernym_paths()[0][::-1], st2.hypernym_paths()[0][::-1]

		# for step in xrange( max(len(hp1), len(hp2)) ):
		# 	if step == len(hp1) or step == len(hp2): break
		# 	if hp1[step] == hp2[step]: ret["WN_COMMON_HYPERNYM"] = ("DIST", 1.0 - step/2.0); break

		for cls in set([x.name for x in s1]) & set([x.name for x in s2]):
			break; ret["WN_COMMON_SYNSET"] = ("Y", 1); break
		else:
			# SIBLING?
			if hp1 == hp2: ret["WN_SIBLING"] = ("Y", -1)

			# ANTONYM?
			if 0 < len( set([x.synset.name for x in s1[0].lemmas[0].antonyms()]) & set([x.synset.name for x in s2[0].lemmas[0].antonyms()]) ):
				ret["WN_ANTONYM"] = ("Y", -1)

			# else:
		# 	if s2[0].name in set([x.name for x in hp1]): ret["WN_ON_PATH"]   = ("Y", 1)
		# 	elif s1[0].name in set([x.name for x in hp2]): ret["WN_ON_PATH"] = ("Y", 1)

	return ( [(v1, v2)], [("%s_%s" % (x, y[0]), y[1]) for x,y in ret.iteritems()] )


def cbScoreFunctionPrnCoref( ctx, p, q ):
	ret = []
	ret += [("PRN_MATCH_Y", 1)] if p[0] == q[0] else [("PRN_MATCH_N", -1)]

	# DISTANCE.
	try:
		ret += [ ("PRN_SENTDIST_%s" % min(1,abs(int(p[1][1].split("x")[0]) - int(q[1][1].split("x")[0]))), 1) ]
			
	except ValueError:
		pass
	
	return ( [(p[1][1], q[1][1])], ret )


def sfFnSelRestr( args, ctx ):
	return []

	
def sfFnUnify( args, ctx ):
	fn1, fn2, coref = args

	if int(fn1[0]) >= int(fn2[0]): return []
	if fn1[0] in fn2[3].split() or fn2[0] in fn1[3].split(): return []
	if 0 < len(set(fn1[3].split()) & set(fn2[3].split())): return []
	if coref[MaxBasicProp+0] == coref[MaxBasicProp+1]: return []
	if coref[MaxBasicProp+0].startswith("_") and coref[MaxBasicProp+1].startswith("_"): return []

	# Argpos???
	
	return [ ("FN_COMMON_FRAME_ROLE_Y", 1) ]

	
def sfRelUnify( args, ctx ):
	ls1, ls2, lcs, lcoref1, lcoref2 = args
	if int(ls1[0]) >= int(ls2[0]): return []
	
	if lcoref1[MaxBasicProp+0] == lcoref1[MaxBasicProp+1]: return []
	if lcoref2[MaxBasicProp+0] == lcoref2[MaxBasicProp+1]: return []
	if 0 < len(set(ls1[2].split()) & set(ls2[2].split())): return []

	#print >>sys.stderr, ls1
	
	return [("REL_%s" % lcs[1], 1)]


def sfSynsetCoref( args, ctx ):
	if args[2][MaxBasicProp+0] == args[2][MaxBasicProp+1] or args[0][0] == args[1][0]: return []
	if args[0][0] in args[1][3].split() or args[1][0] in args[0][3].split(): return []
	if args[0][1] == args[1][1]: return [("WN_COMMON_SYNSET_Y", 1)]
	
	return []


def sfBaseCorefProp( args, ctx ):

	# Named entities
	n1, n2 = args[0][1], args[1][1]
	ret = []

	if int(args[0][0]) >= int(args[1][0]): return []
	
	s1 = corpus.wordnet.synsets( "_".join( n1.split("-")[:-1] ) )
	s2 = corpus.wordnet.synsets( "_".join( n2.split("-")[:-1] ) )

	if n1 == n2: ret += [("PN_SEMCLASS_MATCH_Y", 1)]
	else:        ret += [("PN_SEMCLASS_MATCH_N", -1)]
	
	# if args[2].split()[1] == args[3].split()[1]: ret += [("PN_COMMON_STR", 1)]

	# if 0 < len( set([x.name for x in s1]) & set([x.name for x in s2]) ): ret += [("PNS_WN_CLASS", 1)]
	# else:                                                                ret += [("PNS_WN_NOT_CLASS", 1)]
	
	return ret


def sfModConstr( args, ctx ):
	mod1, mod2, coref = args[0], args[1], args[2]

	mod1, mod2

	
def sfArgConstr( args, ctx ):
	vb1, vb2 = args[0], args[1]

	if args[0][0] == args[1][0]: return []
	
	return [("ARG_CONSTR", 1)]
	
	
def sfSlots( args, ctx ):
	if args[0][0] == args[1][0]: return []
	
	vb1, vb2, n1, n2, v1, v2 = args[0][1].split("-")[-2], args[1][1].split("-")[-2], args[2][1].split("-")[-2], args[3][1].split("-")[-2], args[4][MaxBasicProp+0], args[4][MaxBasicProp+1]
	if v1 in args[1][MaxBasicProp:]: v1, v2 = v2, v1
	if v1 == v2: return []
	
	roledict = {1: "s", 2: "o", 3: "o"}

	def _getSchemas(x):
		v		= g_schema.get(x)
		ret = []
		
		while None != v:
			ret += [v]
			v = g_schema.getnext()
			
		return ret

	try:
		k1, k2	 = "%s-%s,%s" % (vb1, roledict[args[0][MaxBasicProp:].index(v1)], n1), "%s-%s,%s" % (vb2, roledict[args[1][MaxBasicProp:].index(v2)], n2)
		kr1, kr2 = "%s-%s" % (vb1, roledict[args[0][MaxBasicProp:].index(v1)]), "%s-%s" % (vb2, roledict[args[1][MaxBasicProp:].index(v2)])
		s1, s2	 = _getSchemas(k1), _getSchemas(k2)

		if 0 == len(s1): s1 = _getSchemas(kr1)
		if 0 == len(s2): s2 = _getSchemas(kr2)
		
	except ValueError:
		return []

	if 0 == len(s1) or 0 == len(s2): return []

	for sc1 in s1:
		for sc2 in s2:
			if sc1.split(",")[0] == sc2.split(",")[0]:
				return [("SAME_SCHEMA_Y", 1.0/(1+math.exp(-float(sc1.split(",")[2]))))]

	return []
	return [("SAME_SCHEMA_N", -1)]


def cbScoreFunction( ctx ):
	
	ret = []
	p   = henryext.getLiterals( ctx )
	pp  = [x[0] for x in p]
	
	# Functional Words
	for lfs, score in g_funcrel_list:
		if _break(lfs.split( " & " )[1])[0][:-1] not in pp: continue
		
		eq, inst = _getMatchingSets( ctx, [_break(lf.replace( "'", "" )) for lf in lfs.split( " & " )] )
		
		if 2 == len(inst) and 2 <= len(eq["x2"]): ret += ["((\"FUNC_REL_%s\" %f) (^ (= %s %s) ) )" % ("".join(["".join(x) for x in inst[1]]), score, eq["x1"][0], eq["x1"][1]) ]

	# Explicit Non-identity
	for lfs in g_explnids_list:
		eq, inst = _getMatchingSets( ctx, [_break(lf.replace( "'", "" )) for lf in lfs.split( " & " )] )

		if 0 < len(eq) and "" != eq["x"][0] and "" != eq["y"][0]: ret += ["((EXPL_NID 1) (^ (= %s %s) ) )" % (eq["x"][0], eq["y"][0])]
	
	# Argument Constraints
	
		
	return "\n".join(ret)


#
# Preprocessor
#
def cbPreprocess( ctx, obs ):

	if not pa.wnannotate: return []
	
	es_id = 0
	ret		= []

	for obp, obargs, obid in obs:

		# Annotating sense.
		m = re.search( "-(nn|adj|vb)$", obp )
		if None != m:
			for s in corpus.wordnet.synsets( obp.split("-")[-2] ):
				if {"n": "nn", "a": "adj", "v": "vb"}.get(s.pos) == m.group(1) and s.name == obp.split("-")[-2] + "." + s.pos + ".01" :
					es_id += 1
					ret += [("synset%d%08d" % ({"n": 1, "a": 3, "v": 2}[s.pos], s.offset), ["s%d" % es_id, obargs[{"n": 1, "a": 1, "v": 0}[s.pos]]])]

	return ret

#
# Loss function
#
def cbGetLoss( ctx, system, gold ):

	# System coreference decisions.
	system_eq	= [_break(lf)[1] for lf in system.split( " ^ " ) if lf.startswith("=")]
	gold_eq		= [_break(lf)[1] for lf in gold.split( " ^ " ) if lf.startswith("=")]
	
	# Get all the logical variables that represent noun phrases.
	nps			= re.findall( "(-nn|male|female|neuter|thing)\(([^,]+),([^,]+)\)", system )
	nps_var = list(set([np[2] for np in nps]))

	# Check all faults/success in a pairwise manner.
	def _est(x, y, eqs):
		for eq in eqs:
			if x in eq and y in eq: return "Y"
		return "N"

	confmat = {"YY": [], "YN": [], "NY": [], "NN": []}
	wupd    = []
	
	for i, vi in enumerate(nps_var):
		for vj in nps_var[i+1:]:
			cls = _est(vi,vj,gold_eq) + _est(vi,vj,system_eq)
			confmat[ cls ] += [(vi,vj)]
			wupd += [(henryext.getFactorOfUnification(ctx, vi, vj), 0.1 if cls == "NY" and vi.split("x")[0] != vj.split("x")[0] else 1.0)]

	print ["%s:%s" % (k, len(v)) for k, v in confmat.iteritems()]

	total = sum([len(x) for x in confmat.values()])
	
	#return 0.01 * (1.0 * len(confmat["NY"])) / (len(confmat["YN"]) + len(confmat["NY"]) + len(confmat["YY"]) + len(confmat["NN"])) if 0 < total else 1.0

	muc_prec = 1.0 * len(confmat["YY"]) / (len(confmat["YY"]) + len(confmat["YN"])) if (len(confmat["YY"]) + len(confmat["YN"])) != 0 else 1
	muc_rec  = 1.0 * len(confmat["YY"]) / (len(confmat["NY"]) + len(confmat["YY"])) if (len(confmat["NY"]) + len(confmat["YY"])) != 0 else 1

	print muc_prec, muc_rec
	
	#return (1.0*( 1.0 - (2 * muc_prec * muc_rec)/(muc_prec + muc_rec) if muc_prec+muc_rec > 0 else 1 ), [])
	#return (1.0 * math.sqrt((1.0*len(confmat["YN"]) + 1.0*len(confmat["NY"]))/total), [])
	return (1.0*(1.0 * (len(confmat["YN"]) + len(confmat["NY"])) / total if 0 < total else 1), [])

	# Check the coreference outputs

	print system_eq
	
	num_max_score = 0
	num_score			= 0				
	
	for cluster in system_eq:
		for i, ti in enumerate( cluster[1] ):
			if ti.startswith( "_" ): continue
			
			for tj in cluster[1][i+1:]:
				if tj.startswith( "_" ): continue
				num_max_score += 1

				for gcluster in gold_eq:
					if ti in gcluster[1] and tj in gcluster[1]: num_score += 1; break
				else:
					pass #print ti, tj, "should not be unified."

	for cluster in system_ineq:
		for i, ti in enumerate( cluster[1] ):
			if ti.startswith( "_" ): continue
			
			for tj in cluster[1][i+1:]:
				if tj.startswith( "_" ): continue
				num_max_score += 1
				
				for gcluster in gold_eq:
					if ti in gcluster[1] and tj in gcluster[1]: break # print ti, tj, "should be unified."; break
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

