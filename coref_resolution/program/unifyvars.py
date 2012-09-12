
from collections import defaultdict
from lxml import etree

import argparse, re, sys

def main():
	parser = argparse.ArgumentParser( description="Foooo!" )
	parser.add_argument( "--input",   help="Lisp file (s).", type=file )
	parser.add_argument( "--henry",   help="Henry file (s).", type=file )
	parser.add_argument( "--corenlp", help="CoreNLP file (s).", type=file )

	pa = parser.parse_args()

	# Get some mappings.
	map_wordid2vars = defaultdict(set)
	mapper				 = lambda m: re.findall( "(%s)'\(([^)]+)\):[^:]+:[^:]+:\[([0-9ID,-]+)\]" % m, pa.henry.read() )

	for predicate, variables, wordids in mapper("[^)]+"): #mapper( "[^) ]+-nn" ) + mapper( "[^) ]+-vb" ) + mapper("male|neuter|female|thing"):
		for wordid in wordids.split(","):
			wordid_conv = wordid if "ID" not in wordid else repr(int(wordid.split("-ID")[0])*1000+int(wordid.split("-ID")[1]))
			map_wordid2vars[int(wordid_conv)] |= set(variables.split(",") if "-vb" in predicate else [variables.split(",")[1]])

	# Create co-reference chains.
	corenlp	 = etree.parse( pa.corenlp )
	clusters = defaultdict( list )
	
	for chain in corenlp.xpath( "/root/document/coreference/coreference" ):

		heads			= []
		variables = []

		def _getGlobalPos(m): return 1000 * int(m.xpath("sentence")[0].text) + int(m.xpath("head")[0].text)
		def _getHead(m):      return corenlp.xpath( "/root/document/sentences/sentence[@id=\"%s\"]/tokens/token[@id=\"%s\"]/word" % (m.xpath("sentence")[0].text, m.xpath("head")[0].text) )[0].text
		
		for mention in chain.xpath( "mention" ):
			#print >>sys.stderr, etree.tostring(mention)
			heads     += ["%s(%s)" % (_getHead(mention), repr(_getGlobalPos(mention)))]
			variables += map_wordid2vars.get( _getGlobalPos(mention), ["?"] )

		if "?" in variables:
			print >>sys.stderr, pa.input.name + ":", "%d entitie(s) are missing:" % len( filter( lambda x: "?"==x, variables ) ), ", ".join( [heads[i] for i in xrange(len(heads)) if "?" == variables[i]] )

		clean_cluster = [x for x in variables if "?" != x]

		if 1 < len(clean_cluster): clusters[ len(clusters) ] += clean_cluster

	# Create equalities.
	equalities = []
	
	for cluster in clusters.values():
		equalities += ["(= %s)" % (" ".join( cluster ))]

	# Print the lisp.
	lfs = []
	
	for ln in pa.input:
		print ln.rstrip()
		
		if "(name 0)" in ln:
			print "   ", " ".join( equalities ), "; Coreference chain produced by Stanford CoreNLP."

		
if "__main__" == __name__: main()
