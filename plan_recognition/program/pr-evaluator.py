# Usage: scorer.py <result_file>

import argparse

import sys, re

from lxml import etree
from collections import defaultdict

# Special thanks to Parag Singla
EvaluatedArgs = """
(plan_shopping smarket_shopping ?person1 ?thing1 ?place1),(inst ?s smarket_shopping),(shopper ?s ?person1),(thing_shopped_for ?s ?thing1),(store ?s ?place1)
(plan_shopping liqst_shopping ?person1 ?thing1 ?place1),(inst ?s liqst_shopping),(shopper ?s ?person1),(thing_shopped_for ?s ?thing1),(store ?s ?place1)
(plan_shopping shopping ?person1 ?thing1 ?place1),(inst ?s shopping),(shopper ?s ?person1),(thing_shopped_for ?s ?thing1),(store ?s ?place1)
(plan_robbing robbing ?person1 ?place1 ?victim1 ?weapon1 ?thing1),(inst ?r robbing),(robber ?r ?person1),(place_rob ?r ?place1),(victim_rob ?r ?victim1),(weapon_rob ?r ?weapon1),(thing_robbed ?r ?thing1)
(plan_air_travel going_by_plane ?person1 ?luggage1 ?place1 ?tkt1 ?plane1),(inst ?p going_by_plane),(goer ?p ?person1),(plane_luggage ?p ?luggage1),(source_go ?p ?place1),(plane_ticket ?p ?tkt1),(vehicle ?p ?plane1)
(plan_bus_travel going_by_bus ?person1 ?bus1 ?source1 ?dest1 ?driver1 ?tkn1),(inst ?b going_by_bus),(goer ?b ?person1),(vehicle ?b ?bus1),(source_go ?b ?source1),(dest_go ?b ?dest1),(bus_driver ?b ?driver1),(token ?b ?tkn1)
(plan_rest_dining rest_dining ?person1 ?rest1 ?thing1 ?drink1 ?instrument1),(inst ?d rest_dining),(diner ?d ?person1),(restaurant ?d ?rest1),(rest_thing_ordered ?d ?thing1), (rest_thing_drunk ?d ?drink1),(rest_drink_straw ?d ?instrument1)
(plan_drinking drinking ?person1 ?drink1 ?instrument1),(inst ?d drinking),(drinker ?d ?person1),(patient_drink ?d ?drink1),(instr_drink ?d ?instrument1)
(plan_taxi_travel going_by_taxi ?person1 ?taxi1 ?source1 ?dest1 ?td1),(inst ?b going_by_taxi),(goer ?b ?person1),(vehicle ?b ?taxi1),(source_go ?b ?source1),(dest_go ?b ?dest1),(taxi_driver ?b ?td1)
(plan_paying paying ?person1 ?thing1),(inst ?p paying),(payer ?p ?person1),(thing_paid ?p ?thing1)
(plan_jogging jogging ?person1 ?drink1 ?instrument1), (inst ?j jogging), (jogger ?j ?person1), (jog_thing_drunk ?j ?drink1), (jog_drink_straw ?j ?instrument1)
(plan_partying partying ?person1 ?drink1 ?instrument1), (inst ?p partying), (agent_party ?p ?person1), (party_thing_drunk ?p ?drink1),(party_drink_straw ?p ?instrument1)
""".splitlines()

def main():
	parser = argparse.ArgumentParser( description="An evaluation script for plan recognition." )
	parser.add_argument( "--input", help="The input file to be evaluated.", type=file, nargs=1, default=sys.stdin )
	pa = parser.parse_args()
	
	num_total_correct		 = 0
	num_total_system_lfs = 0
	num_total_gold_lfs	 = 0

	tpl_arg_list = dict( [(re.findall( "\(inst .. (.*?)\)", x )[0], re.findall( "\((.*?) .*?\)", x )[2:]) for x in EvaluatedArgs if "" != x] )

	print tpl_arg_list
	
	for result in pa.input:
		problem_name, system, answer = result.split( "\t" )

		#pafilter			 = lambda x: None != re.match( top_plan_regex, x )
		
		#def pafilterBind( bindings ): return lambda x: None != re.match( top_plan_regex + "\((%s)\)" % "|".join( bindings ), x )

		lfs_system = sorted( _shrink( system.split( " ^ " ) ) )
		lfs_gold	 = sorted( _shrink( answer.split( " ^ " ) ) )

		tpl_system = _createTopLevelPlan( lfs_system, tpl_arg_list )
		tpl_gold	 = _createTopLevelPlan( lfs_gold, tpl_arg_list )

		print "-- %s --" % problem_name

		score	= 0
		
		print "Top-level plans in gold data:"
		print "\n".join( [repr(x) for x in tpl_gold] )
		
		print "Top-level plans in system output:"
		print "\n".join( [repr(x) for x in tpl_system] )

		num_correct = 0
		credit      = {}

		for ts in tpl_system:
			for tg in tpl_gold:
				
				num_local_correct = 0
				num_local_max     = 0
				
				if ts[0][0] == tg[0][0]:
					num_local_correct = 1 + len( set(ts[1].keys()) & set(tg[1].keys()) )
					num_local_max     = 1 + len( set(ts[1].keys()) | set(tg[1].keys()) )

				if 0 < num_local_max:
					credit[ ts[0][0] ] = max( credit.get( ts[0][0], 0 ), 1.0 * num_local_correct / num_local_max )

		print credit
		num_correct = sum( credit.values() )
		
		num_total_correct += num_correct
		num_total_system_lfs += len( tpl_system )
		num_total_gold_lfs += len( tpl_gold )
		
		print "Precision:", "%.2f" % (1.0 * num_correct / len( tpl_system )) if 0 < len( tpl_system ) else "-", "(%.2f/%.2f)" % (num_correct, len( tpl_system ))
		print "Recall:   ", "%.2f" % (1.0 * num_correct / len( tpl_gold )                                    ), "(%.2f/%.2f)" % (num_correct, len( tpl_gold ))
		

	prec, rec = 1.0 * num_total_correct / num_total_system_lfs if 0 < num_total_system_lfs else "-", 1.0 * num_total_correct / num_total_gold_lfs
	
	print "-- Total --"
	print "Overall Precision:", "%.2f" % prec if "-" != prec else "-"
	print "Overall Recall:   ", "%.2f" % rec
	print "Overall F-measure:", "%.2f" % ((2*prec*rec) / (prec+rec)) if "-" != prec else "-"

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
def _createTopLevelPlan( lits, tpl_arg_list ):
	ret = []
	
	tlp_g = [_break(lit) for lit in lits if _break(lit)[0][5:] in tpl_arg_list.keys()]
		
	for lit_g in tlp_g:

		# Try to create the complete args.
		tlp_handle_g = lit_g[1][0]
		roles_g      = defaultdict( list )

		for lit in lits:
			if _break(lit)[0] in tpl_arg_list[ lit_g[0][5:] ] and tlp_handle_g == _break(lit)[1][0]:
				roles_g[ _break(lit)[0] ] += [_break(lit)]

		ret += [(lit_g, roles_g)]

	return ret


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
				out_alignments += [dict( [(y, x) for x, y in local_term_aligner.iteritems()] )]
				
				if 0 < len(gold[i+1:]):
					print >>sys.stderr, "found a valid local alignment, go into deeper..."
					_findGoldMatch( out_alignments, out_slots, gold[i+1:], lfs, local_term_aligner, depth+1 )
				else:
					print >>sys.stderr, "Congrats!"
			
		else:
			print >>sys.stderr, head, "No more matching candidates."
			return

		
if "__main__" == __name__: main()

