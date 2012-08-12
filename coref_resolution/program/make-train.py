
from collections import defaultdict

import sys, re, argparse

def main():
	parser = argparse.ArgumentParser( description="Generating equalities." )
	parser.add_argument( "--input", help="Input in drs format.", type=file, nargs=1, default=[sys.stdin] )
	parser.add_argument( "--textid", help="Gold data in CoNLL format." )
	parser.add_argument( "--conll-index", help="CoNLL index.", type=file, nargs=1, dest="conllindex" )
	parser.add_argument( "--showent", help="Show entities and variables mapping.", action="store_true" )

	pa = parser.parse_args()

	if None == pa.textid:     parser.error( "What's text ID?" )
	if None == pa.conllindex: parser.error( "Where's the index?" )

	mapper = dict( [(x.split()[0].split(".")[0], x.split()[1]) for x in pa.conllindex[0]] )
	
	# LOAD THE MAPPING B/W WORDID AND VARIABLES.
	w2v = defaultdict(set)
	inp = pa.input[0].read()
	
	for wids, pred, var in re.findall( "\[([0-9,]+)\]:([^(]+-[nra])\([^,]+,([^),]+)\)", inp ) + \
				re.findall( "\[([0-9,]+)\]:(male|female|person|neuter|thing|his)\([^,]+,([^,)]+)\)", inp ) + \
				re.findall( "\[([0-9,]+)\]:(of|rel)\([^,]+,[^,]+,([^),]+)\)", inp ):
				#re.findall( "\[([0-9,]+)\]:([^(]+-v)\(([^,]+),", inp ):
				
		if pa.showent: print >>sys.stderr, wids, pred, var

		for wid in wids.split( "," ):
			w2v[int(wid)] |= set(["%d%s" % (int(wid)/1000, var)])

	text_id, part_id = pa.textid.split( "-" )
	sent_id					 = 1
	clusters				 = defaultdict(set)
	current_stack    = []
	real_clusters    = defaultdict(list)
	
	for ln in open( mapper[ text_id ] ):
		ln	= ln.split()

		if len(ln) == 0: sent_id += 1;    continue
		elif ln[0] in ["#begin"]: current_text_id = "-".join( re.findall("#begin document \(.*?([a-z]+_[0-9]+)\); part ([0-9]+)", " ".join(ln))[0] ); sent_id = 1

		if "%s-%s" % (text_id, part_id) != current_text_id: continue
		if ln[0] in ["#begin", "#end"]: continue

		global_id = sent_id * 1000 + int(ln[2]) + 1
		#print >>sys.stderr, global_id, ln

		lnins = re.findall("\(([0-9]+)", ln[-1])
		lndel = re.findall("([0-9]+)\)", ln[-1])

		for n in lnins:
			current_stack += [n]
			real_clusters[n] += [global_id]

		for n in current_stack:
			if pa.showent: print >>sys.stderr, n, global_id, w2v[global_id]
			clusters[ n ] |= w2v[global_id]
			
		for n in lndel: current_stack.remove(n)

	variables = []

	for i, cluster in sorted( clusters.iteritems(), key=lambda x: int(x[0]) ):
		scluster = sorted(cluster, key=lambda x: (int(re.findall("^[0-9]+", x)[0]), int(re.findall("^[0-9]+[a-z]+([0-9]+)", x)[0])) )
		
		if len(real_clusters[i]) > len(cluster):
			print "   ; Warning: %d entities are missing: " % (len(real_clusters[i]) - len(cluster)), i, real_clusters[i], scluster

		if 1 >= len(cluster): continue
		
		print "   (= %s) ; Chain %s" % (" ".join( scluster ), i), real_clusters[i]

		variables += [x for x in cluster]

	# variables = list(set(variables))

	# print "  ",
	
	# for i, vari in enumerate( variables ):
	# 	for varj in variables[i:]:

	# 		if vari == varj: continue
			
	# 		for cluster in clusters.values():
	# 			if vari in cluster and varj in cluster: break
	# 		else:
	# 			print "(!= %s %s)" % (vari, varj),

	print
	
if "__main__" == __name__: main()
