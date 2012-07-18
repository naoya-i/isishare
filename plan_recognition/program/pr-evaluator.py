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
				out_alignments += [dict( [(y, x) for x, y in local_term_aligner.iteritems()] )]
				
				if 0 < len(gold[i+1:]):
					print >>sys.stderr, "found a valid local alignment, go into deeper..."
					_findGoldMatch( out_alignments, out_slots, gold[i+1:], lfs, local_term_aligner, depth+1 )
				else:
					print >>sys.stderr, "Congrats!"
			
		else:
			print >>sys.stderr, head, "No more matching candidates."
			return

def main():
	parser = argparse.ArgumentParser( description="An evaluation script for plan recognition." )
	parser.add_argument( "--input", help="The input file to be evaluated.", type=file, nargs=1, default=sys.stdin )
	pa = parser.parse_args()
	
	num_total_correct		 = 0
	num_total_system_lfs = 0
	num_total_gold			 = 0

	tpl_arg_list = dict( [(re.findall( "\(inst .. (.*?)\)", x )[0], re.findall( "\((.*?) .*?\)", x )[2:]) for x in EvaluatedArgs if "" != x] )
	
	for result in pa.input:
		problem_name, system, answer = result.split( "\t" )

		#pafilter			 = lambda x: None != re.match( top_plan_regex, x )
		
		#def pafilterBind( bindings ): return lambda x: None != re.match( top_plan_regex + "\((%s)\)" % "|".join( bindings ), x )

		lfs_system = sorted( _shrink( system.split( " ^ " ) ) )
		lfs_gold	 = sorted( _shrink( answer.split( " ^ " ) ) )

		print "-- %s --" % problem_name

		score	= 0
		
		# lit_g: a top-level plan literal in gold data
		tlp_g = [_break(lit) for lit in lfs_gold if _break(lit)[0][5:] in tpl_arg_list.keys()]
		tlp_s = [_break(lit) for lit in lfs_system if _break(lit)[0][5:] in tpl_arg_list.keys()]

		print >>sys.stderr, "Top-level plans in gold data:", tlp_g
		print >>sys.stderr, "Top-level plans in system output:", tlp_s
		
		for lit_g in tlp_g:
			tlp_handle_g = lit_g[1][0]
			roles_g			 = [_break(lit) for lit in lfs_gold if _break(lit)[0] in tpl_arg_list[ lit_g[0][5:] ] and tlp_handle_g == _break(lit)[1][0]]
			
			local_score			= 0
			local_max_score = 1 + len(roles_g)			
			mapping_score		= defaultdict(int)

			print >>sys.stderr, "Plan matching:", lit_g
			
			# lit_s: a top-level plan literal that matches lit_g in system output.
			for lit_s in [_break(lit) for lit in lfs_system if lit_g[0] == _break(lit)[0] ]:
				
				# "lit_s" is a matching candidate for "lit_g."
				tlp_handle_s = lit_s[1][0]
				log_head = "Plan matching: Role matching: %s: %s -> %s:" % (lit_g, tlp_handle_g, tlp_handle_s)

				# Now searching for the roles of this plan.
				# lit_gr: a role of lit_g in gold data.
				for lit_gr in roles_g:
					
					# lit_sr: a role of lit_g with binding g/s in system output.
					found_roles = 0
					
					for lit_sr in [_break(lit) for lit in lfs_system if lit_gr[0] == _break(lit)[0] and tlp_handle_s == _break(lit)[1][0] and lit_gr[1][1] == _break(lit)[1][1]]:
						print >>sys.stderr, log_head, lit_gr, lit_sr
						mapping_score[ log_head ] += 1
						found_roles += 1

					if 0 == found_roles:
						print >>sys.stderr, log_head, repr(lit_gr) + ": Not found."
						
				print >>sys.stderr, log_head, "# of roles found:", mapping_score[ log_head ], "/", len(roles_g)

						
			if 0 < len(mapping_score.values()):
				score += 1.0 * (1+max( mapping_score.values() )) / local_max_score
				print >>sys.stderr, "Plan matching: %s: Score: %f" % (repr(lit_g), 1.0 * (1+max( mapping_score.values() )) / local_max_score), "(%d/%d)" % (1+max( mapping_score.values() ), local_max_score)

		print "Precision:", score / len(tlp_s) if 0 < len(tlp_s) else 0
		print "Recall:   ", score / len(tlp_g)

		num_total_correct += score
		num_total_gold += len(tlp_g)
		num_total_system_lfs += len(tlp_s)
		
		continue
	
		slots, alignments = {}, []
		_findGoldMatch( alignments, slots, gold, lfs, {} )

		if 0 == len(alignments):
			best_alignment = {}
			lfs_bound      = lfs
		else:
			best_alignment = max( alignments, key=lambda x: len(x.keys()) )
			lfs_bound		 = [_applySignature( lf, best_alignment ) for lf in lfs]
		
		gold = filter( pafilter, gold )

		# What is a variable that should be evaluated?
		bindings = [_break(x)[1][0].replace( "?", "\?" ) for x in gold]
		
		lfs_bound		= filter( pafilterBind(bindings), lfs_bound )
		
		# Superplan
		_superPlanFilter = lambda x, y, z: not x.startswith( "inst_shopping" ) or (x in z or (x.replace("shopping", "smarket_shopping") not in y and x.replace("shopping", "liqst_shopping") not in y))
		lfs_bound   = [x for x in lfs_bound if _superPlanFilter(x, lfs_bound, gold)]

		correct_set	= set(gold)&set(lfs_bound)

		print "Gold:", " ^ ".join( gold )
		print "System:", " ^ ".join( lfs_bound )
		print "Gold ^ System:", " ^ ".join( correct_set )
		
		print "n(G ^ S) =", len( correct_set ), "n(G) =", len( gold ), "n(S) =", len( lfs_bound )
		num_total_correct += len( correct_set ); num_total_system_lfs += len( lfs_bound ); num_total_gold += len( gold )

		print "Precision:", 100.0 * len(correct_set) / len(lfs_bound)  if 0 != len(lfs_bound) else "-"
		print "Recall:   ", 100.0 * len(correct_set) / len(gold)        if 0 != len(gold) else "-"

	print "-- Total --"
	print "Overall Precision:", 100.0 * num_total_correct / num_total_system_lfs
	print "Overall Recall:   ", 100.0 * num_total_correct / num_total_gold

if "__main__" == __name__: main()
