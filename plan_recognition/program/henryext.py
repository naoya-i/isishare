#
# Henry external module for plan recognition experiment
#

import argparse
import sys, re, os
import henryext

from lxml import etree
from collections import defaultdict

def _myfile( x ):
	return os.path.join( g_mydir, x )

g_disj = dict( [(x.strip().split()[0] + x.strip().split()[1], None) for x in open( "/home/naoya-i/work/unkconf2012/plan-disj.tsv" ).readlines() ] )
g_mydir		 = os.path.abspath(os.path.dirname(__file__))



henryext.cppPrint( "hello, pythonier!" )

def _getArgPos( p, t ):
	return re.split( "[(,)]", p ).index(t) - 1

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
			
	ret = []
	vret = []
	
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
			
			#
			if p1id == p2id or (ti == tj and p1id > p2id): continue
			
			# Evidence provided by the same predicate
			if ti != tj and tip == tjp and p1p == p2p:
				ret += [ (-1, "%s:%d" % (p1p, tip), [p1id, p2id]) ]

			# if ti != tj and tip != tjp and p1p == p2p:
			# 	ret += [ (-1, "%s:%d%d" % (p1p, tip, tjp), [p1id, p2id]) ]
				
			# # Disjoint?
			if g_disj.has_key("%s/1%s/1" % (p1p, p2p)) or g_disj.has_key("%s/1%s/1" % (p2p,p1p)):
				ret += [ (-9999, "", [p1id, p2id] ) ]

	#print ti, tj, vret
	
	return ret


#
def cbGetLoss( system, gold ):

	lfs			 = sorted( _shrink( system.split( " ^ " ) ) )
	gold_not = sorted( filter( lambda x: x.startswith( "!" ), gold.split( " ^ " ) ) )
	gold_pos = sorted( filter( lambda x: not x.startswith( "!" ), gold.split( " ^ " ) ) )

	num_pos_loss, num_neg_loss = 0, 0

	# Loss for negative literals.
	for lit in gold_not:
		lit = _break( _break(lit)[1][0] + ")" )

		negatives = filter( lambda x: x.split("(")[0] == lit[0], system.split( " ^ " ) )
			
		if len(negatives) > 0:
			print >>sys.stderr, "Negative literal found:", negatives

		num_neg_loss += len(negatives)
	
	slots, alignments = {}, []
	_findGoldMatch( alignments, slots, gold_pos, lfs, {} )

	if 0 < len( alignments ) and 0 == num_neg_loss: return 0

	return 10

	# 	best_alignment = max( alignments, key=lambda x: len(x.keys()) )
	# 	lfs_bound			 = [_applySignature( lf, best_alignment ) for lf in lfs]
	# else:
	# 	best_alignment = {}
	# 	lfs_bound			 = lfs

	# correct_set	= set(gold)&set(lfs_bound)
	
	gold_predicates			 = [_break(lf)[0] for lf in gold_pos]
	gold_not_predicates	 = [_break(lf)[0] for lf in gold_not]
	system_predicates		 = [_break(lf)[0] for lf in lfs]
	# correct_predicates = []
	# missing_predicates = []
	
	# for p1 in gold_predicates:
	# 	for p2 in system_predicates:
	# 		if p1 == p2: correct_predicates += [p1]; break
	# 	else:
	# 		missing_predicates += [p1]

	# num_correct_args		 = 0
	# num_correct_args_max = 0

	# for lf in gold:
	# 	for t in _break(lf)[1]:
	# 		if t in best_alignment.values(): num_correct_args += 1
	# 		num_correct_args_max += 1

	num_pos_loss, num_neg_loss = 0, 0

	# Loss for negative literals.
	for lit in gold_not:
		lit = _break( _break(lit)[1][0] + ")" )

		negatives = filter( lambda x: x.split("(")[0] == lit[0], system.split( " ^ " ) )
			
		if len(negatives) > 0:
			print >>sys.stderr, "Negative literal found:", negatives

		num_neg_loss += len(negatives)

	# Loss for positive literals.
	missing_predicates = []
	
	for p in gold_predicates:
		
		positives = filter( lambda x: x.split("(")[0] == p, system.split( " ^ " ) )

		if 0 == len(positives):
			num_pos_loss += 1
			missing_predicates += [p]

	# Create a mapping
	v2h				= defaultdict( list )
	unified   = {}
	variables = set()
	
	for lit in system.split( " ^ " ):
		for t in _break( lit )[1]:
			v2h[t]		+= [_break( lit )]
			variables |= set([t])
		
		if lit.startswith( "=" ):
			for ti in _break(lit)[1]:
				for tj in _break(lit)[1]:
					unified[ (ti, tj) ] = None
					unified[ (tj, ti) ] = None
		
	# Loss for variable unification.
	num_unif_loss = 0

	variables = list(variables)
	
	for i, ti in enumerate( variables ):
		for tj in variables[i+1:]:

			# Is it unified based on the correct evidences?
			if not unified.has_key( (ti, tj) ):
				tgp, tgy = "", -1
				
				for p in v2h.get( ti, [] ):
					if p[0] in gold_predicates:
						tgy = _getArgPos( "%s(%s)" % (p[0], ",".join(p[1])), ti )

						for q in v2h.get( tj, [] ):
							if q[0] == p[0] and tgy == _getArgPos( "%s(%s)" % (q[0], ",".join(q[1])), tj ):
								print p[0], ",".join(p[1]), ti, tj
								num_unif_loss += 1
								break

					
		
	print >>sys.stderr, "-- Loss report --"
	print >>sys.stderr, "# of -:", num_neg_loss
	print >>sys.stderr, "# of +:", num_pos_loss
	print >>sys.stderr, "# of u:", num_unif_loss

	print >>sys.stderr, "missing preds:", missing_predicates
	
	#return num_neg_loss + (len(slots.keys()) - len(best_alignment.keys())) + (len(gold_predicates) - len(correct_predicates))  #(len(gold) - len(correct_set))
	#return num_neg_loss + (len(gold) - len(correct_set))
	return num_pos_loss + num_unif_loss # + num_neg_loss 


# "PRED(ARG1, ARG2, ARG3, ...)" => ("PRED", ["ARG1", "ARG2", "ARG3", ...])
def _break(lf):	lf = re.match( "(.*?)\((.*?)\)", lf ); return (lf.group(1), lf.group(2).split(","))

# "PRED(ARG1, ARG2, ARG3)" + {ARG1: x, ARG2: y} => "PRED(x, y, ARG3)"
def _applySignature( lf, signature ): lf = _break(lf); return "%s(%s)" % (lf[0], ",".join( [signature.get( t, t ) for t in lf[1]] ) )

# ["a(x)", "b(y)", "=(x, y)"] => ["a(x)", "b(x)"]
def _shrink( lfs ):
	signature	= {}

	for eq in lfs:
		if not eq.startswith( "=" ): continue
		eq   = _break(eq)
		eq_c = filter( lambda v: v[0].isupper(), eq[1] )
		eq_k = filter( lambda v: "_" != v[0], eq[1] )
		rep  = eq_c[0] if 0 < len(eq_c) else eq_k[0] if 0 < len(eq_k) else eq[1][0]

		for v in eq[1]: signature[v] = rep
	
	return list( set([_applySignature( lf, signature ) for lf in lfs if not lf.startswith("=")]) )

#
def _findGoldMatch( out_alignments, out_slots, gold, lfs, bind_history, depth = 1 ):

	for i, glf_i in enumerate(gold):
		sglf = _break( glf_i )
		head = "%s %s %s:" % (("-" * depth), str(bind_history), glf_i)

		for t in sglf[1]: out_slots[t] = ""
		
		print >>sys.stderr, head

		# Search for the literal with the same predicate with glf_i.
		for lf in lfs:
			slf = _break( lf )

			if sglf[0] != slf[0]: continue

			print >>sys.stderr, head, "Matching %s..." % lf,
			
			local_term_aligner = dict(bind_history)

			for j, term_j in enumerate(sglf[1]):
				if local_term_aligner.has_key( term_j ) and slf[1][j] != local_term_aligner[ term_j ]:
					print >>sys.stderr, "oops at %s != %s" % (slf[1][j], local_term_aligner[ term_j ])
					break
				else:
					local_term_aligner[ term_j ] = slf[1][j]

			else:
				out_alignments += [local_term_aligner]
				
				if 0 < len(gold[i+1:]):
					print >>sys.stderr, "found a valid local alignment, go into deeper..."
					_findGoldMatch( out_alignments, out_slots, gold[i+1:], lfs, local_term_aligner, depth+1 )
				else:
					print >>sys.stderr, "Congrats!"
			
		else:
			print >>sys.stderr, head, "No more matching candidates."
			return

