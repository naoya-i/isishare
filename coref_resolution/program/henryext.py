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
parser.add_argument( "--loss", help="Loss function (f1/disagree).", default="disagree" )
parser.add_argument( "--argcons", help="Activate argument constraints.", action="store_true" )
parser.add_argument( "--condunif", help="Activate conditional unification constraints.", type=file, nargs="+" )
parser.add_argument( "--funcrel", help="Activate functional relations constraints.", type=file, nargs=1 )
parser.add_argument( "--ineq", help="Activate explicit non-identity constraints.", type=file, nargs=1 )
parser.add_argument( "--nedisj", help="Activate named entities disjointness constraints.", action="store_true" )
parser.add_argument( "--wndisj", help="Activate WordNet-based disjointness constraints.", action="store_true" )
parser.add_argument( "--nofuncrel", help="Do not use functional relation KB.", action="store_true" )
parser.add_argument( "--noexplident", help="Do not use explicit non-identity KB.", action="store_true" )
parser.add_argument( "--nomodality", help="Do not use modality constraints.", action="store_true" )
parser.add_argument( "--noinc", help="Do not use incompatibility constraints.", action="store_true" )
parser.add_argument( "--noargineq",  help="Do not use argument inequality constraints.", action="store_true" )
parser.add_argument( "--classicalmerge", help="Use classical unification strategy.", action="store_true" )
parser.add_argument( "--wnannotate", help="Annotate synset predicates in preprocessing.", action="store_true" )
parser.add_argument( "--ncannotate", help="Annotate narrative schema predicates in preprocessing.", action="store_true" )
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
print >>sys.stderr, "Loading WordNet antonyms..."

g_wnanto = {}

for ln in open(_myfile("../data/wn-anto.tsv")):
	ln																 = ln.split()
	g_wnanto["%s-%s" % (ln[0], ln[1])] = None

#
print >>sys.stderr, "Loading WordNet hierarchy..."

g_wnhier = defaultdict(list)

for ln in open(_myfile("../data/wn-hyp.lisp")):
	ln = re.findall( "\(synset([0-9]+) .*?\)\) \(synset([0-9]+) .*?\)\) \)", ln )
	g_wnhier[ ln[0][1] ] += [ln[0][0]]
	
#
g_fnsr = {}

print >>sys.stderr, "Loading FrameNet selectional restriction..."

for ln in open(_myfile("../data/fn-sr.lisp")):
	ln = re.findall( "\(=> \((.*?) s x :([0-9.]+)\) \((FN[^ ]+) (.*?)\)", ln )

	if 1 == len(ln):
		g_fnsr["%s-%s" % (ln[0][0], ln[0][2])] = (ln[0][0], float(ln[0][1]), ln[0][2], ln[0][3].split())
	

#
print >>sys.stderr, "Loading conditional unification predicates..."

g_conds = [x.strip() for x in open(_myfile("../data/cu-preds.txt"))]

		
#
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
				score_for_er = 0.0
				
				for filler, filler_score in re.findall( "([^ ]+) ([0-9.-]+)", rolefillers ):
					score_for_er += float(filler_score)
					if "schema" in pa.caching: maker.add( "%s,%s" % (e, filler), "%d-%d,%s,%f" % (schema_id, role_id, events, float(filler_score) + scores_dict[e[:-2]]) )
					
				if "schema" in pa.caching: maker.add( e, "%d-%d,%s,%f" % (schema_id, role_id, events, score_for_er))
				

	if "schema" in pa.caching: maker.finish()
		

#
# RESOURCE: CONDITIONAL UNIFICATION
print >>sys.stderr, "Loading conditional unification files..."
g_cu = []

if None != pa.condunif:
	print >>sys.stderr, "Activated: CONDITIONAL UNIFICATION"
	
	for f in pa.condunif:
		g_cu += re.findall( "set_condition\((.*?)'/", f.read() )
	
print >>sys.stderr, "Loading word frequency and abstraction levels..."
g_word_freq	= dict( [(x.split()[1], -1.0/math.log( int(x.split()[3]) )) for x in open(_myfile("../data/entriesWithoutCollocates.txt")) if 5 == len(x.split())] )
g_word_abst = dict( [(x.split()[0][:-1], int(x.split()[1])/18.0) for x in open(_myfile("../data/WN_abstraction_level.txt")) if 2 == len(x.split())] )

#
# RESOURCE: FUNCTIONAL RELATIONS
g_funcrel_list = []
g_funcrel			 = defaultdict( list )

if not pa.nofuncrel:
	print >>sys.stderr, "Loading functional relations..."

	g_funcrel_list = [(ln.split("\t")[0], (1/6406.84)*float(ln.split("\t")[1])) for ln in open(_myfile("../data/func_relations-patterns-uniq.txt")) if 2 == len(ln.split("\t"))]

	for ln in open(_myfile("../data/func_relations-patterns-uniq.txt")):
		ln, ln_broken = ln.strip().replace( "'", "" ), [_break(lit) for lit in ln.strip().replace( "'", "" ).split( " & " ) ]

		for lit in ln_broken:
			g_funcrel[ lit[0] ]	+= [(ln_broken, float(ln.split( "\t" )[1] if "\t" in ln else 0.0))]

#
# RESOURCE: INEQUALITIES
g_explnids_list = []
g_explicit_non_ids = []

if not pa.noexplident:
	print >>sys.stderr, "Loading explicit-nonidentity predicates..."

	g_explnids_list = [ln.split( "x!=y => " )[1] for ln in open(_myfile("../data/inequality.kb")) if 2 == len( ln.split( "x!=y => " ) )]

	for ln in open(_myfile("../data/inequality.kb")):
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

#
print >>sys.stderr, "Loading frame disjointness axioms..."

g_fndisj = {}

for ln in open(_myfile("../data/fn-disj.tsv")):
	ln = ln.split()
	
	for p1 in ln:
		for p2 in ln:
			if p1 == p2: continue
			g_fndisj["%s-%s" % (p1, p2)] = None
		
if "argv" in dir(sys): parser.print_help(); sys.exit()

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


def cbScoreFunction( ctx ):
	
	ret		= []
	set_p = henryext.getLiterals( ctx )
	
	# FUNCTIONAL WORDS
	for lfs, score in g_funcrel_list:
		eq, inst = _getMatchingSets( ctx, [_break(lf.replace( "'", "" )) for lf in lfs.split( " & " )] )

		if 2 == len(inst) and 2 <= len(eq["x2"]):
			ret += [([["!c%s %s" % (eq["x2"][0], eq["x2"][1]), "c%s %s" % (eq["x1"][0], eq["x1"][1])]], "FUNC_REL", -1)]

	# Explicit Non-identity
	for lfs in g_explnids_list:
		eq, inst = _getMatchingSets( ctx, [_break(lf.replace( "'", "" )) for lf in lfs.split( " & " )] )
		
	 	if 0 < len(eq) and "" != eq["x"][0] and "" != eq["y"][0]:
			ret += [([["c%s %s" % (eq["x"][0], eq["y"][0])]], "EXPLICIT_NONIDENT", -1)]
	
	same_pred_args = {}
			
	for p in set_p:
		if henryext.isTimeout(ctx): return ret
		if p[0].startswith("=") or p[0] == "!=": continue

		# COST FOR p.
		def _getDepth(x):
			return 0 if "" == x[4].strip() else len(x[4].split(","))

		ret += [([["p%d" % p[2]]], "HYPOTHESIZED_%s" % (p[0].split("-")[-1]), -p[5])]

		# CREATE EXPLANATION FACTORS FOR p.
		dnf_expl = []
		
		for q in set_p:
			if q[0].startswith("=") or q[0] == "!=": continue
			if p[2] == q[2]:         continue

			if "" != p[4] and "" != q[4]:
				
				# IF THEY ARE EXPLAINING THE SAME THING, JUST IGNORE THEM. (p => q, p => q)
				if 0 < len(set(p[4].split(",")) & set(q[4].split(","))): continue
				
				# SELF-EXPLANATION IS PROHIBITED. (p => q => p)
				if repr(q[2]) in p[4].split(","): continue
				
			psuf, qsuf		 = re.findall("-([^-]+)$", p[0]), re.findall("-([^-]+)$", q[0])
			psuf, qsuf		 = (psuf[0] if 0 < len(psuf) else ""), (qsuf[0] if 0 < len(qsuf) else "")
			fc_cooc				 = ["p%d" % p[2], "p%d" % q[2]]
			fc_cooc_vu0		 = fc_cooc + ["c%s %s" % (p[1][0], q[1][0])]
			fc_cooc_vu1		 = fc_cooc + ["c%s %s" % (p[1][1], q[1][1])]
			fc_cooc_vuall1 = fc_cooc + (["c%s %s" % (p[1][i], q[1][i]) for i in xrange(1,len(p[1]))] if 1 < len(p[1]) and len(p[1]) == len(q[1]) else [])
			fc_cooc_vuall  = fc_cooc + (["c%s %s" % (p[1][i], q[1][i]) for i in xrange(len(p[1]))] if 1 < len(p[1]) and len(p[1]) == len(q[1]) else [])

			# ARGUMENTS AT THE SAME OBSERVABLE PREDICATES.
			# if 1 < len(p[1]) and len(p[1]) == len(q[1]):
			# 	for i in xrange(1,len(p[1])):
			# 		if same_pred_args.has_key("%s-%s" % (q[1][i], p[1][i])) or same_pred_args.has_key("%s-%s" % (p[1][i], q[1][i])): continue

			# 		for c1 in henryext.getLiteralsFromTerm(ctx, p[1][i]):
			# 			for c2 in henryext.getLiteralsFromTerm(ctx, q[1][i]):
			# 				if c1[2] == c2[2] and "" == c1[4] and "" == c2[4]:
			# 					ret += [([["c%s %s" % (p[1][i], q[1][i])]], "UNIFY_SAME_PRED_ARGS", -1)]
			# 					same_pred_args["%s-%s" % (p[1][i], q[1][i])] = 1
			# 					break

			#
			# EXPLANATION FOR p.
			if p[0] != q[0] and repr(p[2]) in q[4].split(","): dnf_expl += [(fc_cooc, "", 1)]

			# SYNSET CAN BE EXPLAINED BY PRONOUNS.
			# if p[0][0] == "~" and q[0].startswith("synset"):
			# 	prn, nn = p, q

			# 	if "3" != nn[0][6]:
			# 		dnf_expl += [(fc_cooc_vuall, "PRONOUN_%s_REF_%s" % (prn[0], nn[0]), 1)]
				
				# try: dnf_expl += [(fc_cooc_vu1, "PRONOUN_%s_SENTDIST_%s" % (prn[0], min(1,abs(int(p[1][1].split("x")[0]) - int(q[1][1].split("x")[0])))), 1) ]
				# except ValueError: pass

			
			#
			# EXPLANATION BY UNIFICATION.
				
			# BELOW ARE EXPLANATION BY UNIFICATION; AVOID DOUBLE-COUNT.?
			#if p[2] <= q[2]: continue
			# if p[0] == q[0]: dnf_expl += [(fc_cooc_vuall1, "WWWWW", 1)]
			# continue
			f_uexpl_created	= False
			_bothStartsWith = lambda x: p[0].startswith(x) and q[0].startswith(x)
			_samePreds      = lambda: p[0] == q[0]

			# CLASSICAL UNIFICATION STRATEGY?
			if pa.classicalmerge:
				if psuf not in "nn adj vb rb".split():  continue
				if _samePreds(): dnf_expl += [(fc_cooc_vuall, "UNIFY_PROPOSITIONS", 1)]
				continue
			
			# NARRATIVE SCHEMAS.
			if p[0] == q[0] and _bothStartsWith("Script"): dnf_expl += [(fc_cooc_vuall1, "NC_COMMON_Y", 1)]; f_uexpl_created = True
					
			# WORDNET FEATURE.
			if _bothStartsWith("synset"):
				if p[0] == q[0]:
					dnf_expl += [(fc_cooc_vuall, "WN_COMMON_SYNSET_Y", 1)]; f_uexpl_created = True
				elif g_wnanto.has_key("%s-%s" % (q[0][7:], p[0][7:])) or g_wnanto.has_key("%s-%s" % (p[0][7:], q[0][7:])):
					if not pa.noinc: ret += [([fc_cooc_vuTTT1], "WN_ANTONYMOUS_SYNSET_Y", -1)]
				else:
					prnt1, prnt2 = g_wnhier.get( p[0][6:] ), g_wnhier.get( q[0][6:] )
					if None != prnt1 and prnt1 == prnt2:
						if not pa.noinc: ret += [([fc_cooc_vu1], "WN_SIBLING_SYNSET_Y", -1)]
						
			# FRAMENET FEATURE.
			if p[0] == q[0] and _bothStartsWith("FN"):
				dnf_expl += [(fc_cooc_vuall1, "FN_%s_COMMON_Y" % p[0], 1)]; f_uexpl_created = True
					
			# PRONOUN & PRONOUN
			if q[0][0] == "~" and p[0][0] == "~" and q[0] == p[0]:
				dnf_expl += [(fc_cooc_vuall, "PRONOUN_MATCH_%s_Y" % p[0], 1)]; f_uexpl_created = True
				# try: dnf_expl += [(fc_cooc_vu1, "PRONOUN_%s_SENTDIST_%s" % (p[0], min(1,abs(int(p[1][1].split("x")[0]) - int(q[1][1].split("x")[0])))), 1) ]
				# except ValueError: pass

			# OTHER LINGUISTIC FEATURES.
			if psuf == qsuf and psuf in "nn adj vb rb".split() and len(p[1]) == len(q[1]):
				
				if p[0] == q[0]:
					if "vb" == psuf:
						num_args = min(3,len(p[1])-1)

						dnf_expl += [(fc_cooc_vuall, "PROP_MATCH_%s" % psuf, 1)]; f_uexpl_created = True
						
						# ret += [([fc_cooc + ["c%s %s" % (p[1][1+a], q[1][1+a])]], "PROP_MATCH_%s_ARG%d" % (psuf, a), -1) for a in xrange(num_args)]

						# # WORDFREQ AND ABSTRACTION LEVELS.
						# if g_word_abst.has_key(p[0]):                ret += [([fc_cooc + ["c%s %s" % (p[1][1+a], q[1][1+a])]], "PROP_MATCH_%s_ARG%d_ABST" % (psuf, a), -g_word_abst[p[0]]) for a in xrange(num_args)]
						# if g_word_freq.has_key(p[0].split("-")[-2]): ret += [([fc_cooc + ["c%s %s" % (p[1][1+a], q[1][1+a])]], "PROP_MATCH_%s_ARG%d_FREQ" % (psuf, a), -g_word_freq[p[0].split("-")[-2]]) for a in xrange(num_args)]
						
					else:
						dnf_expl += [(fc_cooc_vuall, "PROP_MATCH_%s" % psuf, 1 if "in" != psuf else -1)]; f_uexpl_created = True

						# # WORDFREQ AND ABSTRACTION LEVELS.
						# if g_word_abst.has_key(p[0]):                ret += [([fc_cooc_vuall1], "PROP_MATCH_ABST_%s" % psuf, -g_word_abst[p[0]])]
						# if g_word_freq.has_key(p[0].split("-")[-2]): ret += [([fc_cooc_vuall1], "PROP_MATCH_FREQ_%s" % psuf, -g_word_freq[p[0].split("-")[-2]])]
				
						
					if "in" == psuf and 3 <= len(p[1]) and len(p[1]) == len(q[1]):
						ret += [([fc_cooc + ["c%s %s" % (p[1][1], q[1][1]), "!c%s %s" % (p[1][2], q[1][2])]], "PREP_BREAK_RULE", -1)]
						

				if "vb" == psuf:
					# SELECTIONAL RESTRICTION FROM LARGE CORPORA (TO BE...).
					pass
					
				# Prop + WN
				if "nn" == psuf:
					pat, qat = [pp for pp in henryext.getLiteralsFromTerm(ctx, p[1][1]) if pp[0].startswith("@")], [qq for qq in henryext.getLiteralsFromTerm(ctx, q[1][1]) if qq[0].startswith("@")]

					# if p[0] != q[0]:
					# 	if len(pat) > 0 and len(qat) > 0: ret += [([fc_cooc_vu1], "DIFFERENT_PROPERNAMES_UNIFIED", -1)]

					pat, qat = [], []
						
			# BOXER AUX.
			# if "@" == p[0][0] and p[0] == q[0]:
			# 	dnf_expl += [(fc_cooc_vuall, "BOXER_AUX_%s" % p[0], -1)]; f_uexpl_created = True

			if _samePreds() and not f_uexpl_created:
				print >>sys.stderr, p, q
			# 	#dnf_expl += [(fc_cooc_vuall1, "UNIFY_PROPOSITIONS", 1)]; f_uexpl_created = True

			#
			# CONSTRAINTS
				
			# ARGUMENT CONSTRAINTS.
			if not pa.noargineq:
				if p[0] == q[0] and len(p[1]) == len(q[1]):
					eas = ["%s%s %s" % ("c" if 0==i else "!c", p[1][i], q[1][i]) for i in xrange(len(p[1])) if "e" in p[1][i] or "e" in q[1][i]]

					if 2 <= len(eas):
						ret += [([fc_cooc + eas], "ARGUMENT_CONSTR", -1)]

				# EVENT-DENOTING VARIBLE CONSTRAINTS.
				if _samePreds() and psuf == qsuf == "vb":
					try:
						ret += [([fc_cooc_vu0 + ["!c%s %s" % (p[1][i], q[1][i])]], "ARGUMENT_CONSTR", -1) for i in xrange(1, len(p[1]))]
					except IndexError:
						pass
					
					
			# MODALITY CONSTRAINTS.
			if not pa.nomodality:
				if psuf == qsuf == "vb" and p[0] == q[0]:
					try:
						ps, qs = [x for x in henryext.getLiteralsFromTerm(ctx, p[1][0]) if (x[0].endswith("-M") and x[1][1] == p[1][0]) or (x[0].endswith("vb") and x[1][2] == p[1][0])], \
								[x for x in henryext.getLiteralsFromTerm(ctx, q[1][0]) if (x[0].endswith("-M") and x[1][1] == q[1][0]) or (x[0].endswith("vb") and x[1][2] == q[1][0])]

						if len(ps) > 0 or len(qs) > 0:
							ret += [([fc_cooc + ["c%s %s" % (p[1][i], q[1][i]) for i in xrange(0,len(p[1])) if "u" not in p[1][i] or "u" not in q[1][i]]], "MODALITY_CONSTR", -1)]
					except IndexError:
						pass
				
				
			# FRAMENET FRAME-FRAME DISJOINTNESS.
			if g_fndisj.has_key("%s-%s" % (p[0], q[0])):
				ret      += [([fc_cooc_vu0], "FN_DISJOINT_FRAMES", -1)]
		
			# FRAMENET SELECTIONAL RESTRICTION.
			if (p[0].startswith("synset") and q[0].startswith("FN")) or (q[0].startswith("FN") and p[0].startswith("synset")):
				syn, fn = (p, q) if p[0].startswith("synset") and q[0].startswith("FN") else (q, p)
				fnsr = g_fnsr.get( "%s-%s" % (syn[0], fn[0]) )
				if None != fnsr: 
					ret += [([fc_cooc + ["c%s %s" % (fn[1][fnsr[3].index("x")], syn[1][1])]], "FN_%s_SEL_RESTR_Y" % fn[0], -1+fnsr[1])]			
				

		# CREATE FEATURE FOR EACH DISJUNCTIVE CLAUSE
		# for disj in dnf_expl:
		#  	ret += [([disj[0]], disj[1], -0.1)]

		# CREATE FEATURE FOR DNF.
		ret += [([disj[0] for disj in dnf_expl], "EXPLAINED", p[5])]
			
	return ret


g_uk = 0

def _getSchemaLiterals(k, arg, parents):
	global g_uk
	g_uk += 1
	sc	= g_schema.get(k)
	ret = []
	
	while None != sc:
		sargs = ["n%d" % g_uk]
		g_uk += 1

		for j in xrange(4):
			sargs += [arg if j == int(sc.split(",")[0].split("-")[1]) else "_n%d" % g_uk]
			g_uk += 1

		ret += [("Script%s" % sc.split(",")[0].split("-")[0], sargs, parents)]
		sc = g_schema.getnext()
		
	return ret

#
# Preprocessor
#
def cbPreprocess( ctx, obs ):

	ret		= []
	
	if pa.wnannotate:
		es_id = 0

		for obp, obargs, obid in obs:

			# Annotating WordNet predicates.
			m = re.search( "-(nn|adj|vb)$", obp )
			if None != m:
				try:
					s = corpus.wordnet.synset("%s.%s.01" % (obp.split("-")[-2], {"nn": "n", "adj": "a", "vb": "v"}.get(obp.split("-")[-1]) ))
					es_id += 1
					ret += [("synset%d%08d" % ({"n": 1, "a": 3, "v": 2}.get(s.pos, 0), s.offset), ["s%d" % es_id, obargs[{"n": 1, "a": 1, "v": 0}.get(s.pos, 0)]], [])]
				except corpus.reader.WordNetError: continue

	if pa.ncannotate:
		for obp, obargs, obid in obs:
			if obp.endswith("-vb"):

				# Search for the narrative schema.
				for i in xrange(1,len(obargs)):
					if "u" in obargs[i]: continue
					
					argpred = [x for x in henryext.getLiteralsFromTerm(ctx, obargs[i]) if x[0].endswith("-nn") or x[0].startswith("~")]

					if 0 == len(argpred):
						ret += _getSchemaLiterals("%s-%s" % (obp.split("-")[-2], {1: "s", 2: "o", 3: "o"}[i]), obargs[i], [obid])
					else:
						for ap in argpred:
							if ap[0].startswith("~"):
								ret += _getSchemaLiterals("%s-%s" % (obp.split("-")[-2], {1: "s", 2: "o", 3: "o"}[i]), obargs[i], [obid, ap[2]])
							else:
								ret += _getSchemaLiterals("%s-%s,%s" % (obp.split("-")[-2], {1: "s", 2: "o", 3: "o"}[i], ap[0].split("-")[-2]), obargs[i], [obid, ap[2]])
											
	return ret

#
# Loss function
#
def cbGetLoss( ctx, system, gold ):

	# System coreference decisions.
	system_eq	= [_break(lf)[1] for lf in system.split( " ^ " ) if lf.startswith("=")]
	gold_eq		= [_break(lf)[1] for lf in gold.split( " ^ " ) if lf.startswith("=")]
	
	# Get all the logical variables that represent noun phrases.
	nps			 = re.findall( "(-nn|male|female|neuter|thing)\(([^,]+),([^,]+)\)", system )
	nps_var	 = list(set([np[2] for np in nps]))
	nps_gold = []

	for eq in gold_eq: nps_gold += eq

	print nps_gold
	
	# Check all faults/success in a pairwise manner.
	def _est(x, y, eqs):
		for eq in eqs:
			if x in eq and y in eq: return "Y"
		return "N"

	confmat = {"YY": [], "YN": [], "NY": [], "NN": []}
	wupd    = []
	
	for i, vi in enumerate(nps_var):
		for vj in nps_var[i+1:]:
			if vi not in nps_gold or vj not in nps_gold: continue
			
			cls = _est(vi,vj,gold_eq) + _est(vi,vj,system_eq)
			confmat[ cls ] += [(vi,vj)]
			wupd += [(henryext.getFactorOfUnification(ctx, vi, vj), 0.1 if cls == "NY" and vi.split("x")[0] != vj.split("x")[0] else 1.0)]

	print ["%s:%s" % (k, len(v)) for k, v in confmat.iteritems()]

	total = sum([len(x) for x in confmat.values()])
	
	#return 0.01 * (1.0 * len(confmat["NY"])) / (len(confmat["YN"]) + len(confmat["NY"]) + len(confmat["YY"]) + len(confmat["NN"])) if 0 < total else 1.0

	muc_prec = 1.0 * len(confmat["YY"]) / (len(confmat["YY"]) + len(confmat["YN"])) if (len(confmat["YY"]) + len(confmat["YN"])) != 0 else 1
	muc_rec  = 1.0 * len(confmat["YY"]) / (len(confmat["NY"]) + len(confmat["YY"])) if (len(confmat["NY"]) + len(confmat["YY"])) != 0 else 1

	print muc_prec, muc_rec

	if "f1" == pa.loss:
		return (1.0*( 1.0 - (2 * muc_prec * muc_rec)/(muc_prec + muc_rec) if muc_prec+muc_rec > 0 else 1 ), [])
	
	#return (1.0 * math.sqrt((1.0*len(confmat["YN"]) + 1.0*len(confmat["NY"]))/total), [])

	if "disagree" == pa.loss:
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

