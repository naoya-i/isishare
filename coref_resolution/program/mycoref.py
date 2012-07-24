
from lxml import etree
from collections import defaultdict

import argparse, sys, os, re


def mycoref( target, pa ):

	facts = []
	henry = open( pa.henry[0] ).read()
	
	# Load mapping b/w entity variables and word id.
	map_var_wordid = defaultdict( list)
	mapper				 = lambda m: re.findall( "([^) ]+-%s')\(([^)]+)\):[^:]+:[^:]+:\[([^]]+)\]" % m, henry )
	
	for predicate, variables, wordids in mapper( "nn" ) + mapper( "vb" ):
		for wordid in wordids.split(","):
			map_var_wordid[variables.split(",")[0] if "vb'" in predicate else variables.split(",")[1] ] += [wordid]

	# List the sentences.
	xml_root = etree.Element( "coreference-result", attrib={"text": target} )
	chain_id = 0
	
	for obs_sent in re.findall( "(%s_[0-9]+)\]" % target, henry ):
		try:
			xml_ret					= etree.parse( os.popen( "%s -m infer %s -d 2 -T 10 -p %s -t 8 -b %s/kb.da -i %s -e %s" % ( pa.reasoner, pa.input[0], obs_sent, pa.datadir[0], pa.infmethod, pa.extmod ) ) )

		except:
			print >>sys.stderr, "Parse error:", target
			continue
		
		hypothesis			= xml_ret.xpath( "/henry-output/result-inference/hypothesis" )[0].text
		
		for lit in hypothesis.split( " ^ " ):
			if "=(" in lit:
				xml_chain							 = etree.Element( "chain", attrib={"id": str(chain_id)} ); 	  xml_root.append( xml_chain )
				xml_chain_vars				 = etree.Element( "variables" ); xml_chain.append( xml_chain_vars )
				xml_chain_wordids			 = etree.Element( "wordids" );   xml_chain.append( xml_chain_wordids )
				xml_chain_vars.text    = re.findall( "=\((.*?)\)", lit )[0]
				xml_chain_wordids.text = ",".join( [ ",".join(map_var_wordid.get(x, "?")) for x in re.findall( "=\((.*?)\)", lit )[0].split(",") ] )

				chain_id += 1
				
		xml_root.append( xml_ret.xpath( "/henry-output" )[0] )
		
	print etree.tostring( xml_root, pretty_print=True )
			
	return facts



def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Input in Henry format.", nargs=1 )
	parser.add_argument( "--henry", help="File mapping between word ids and henry literals.", nargs=1 )
	parser.add_argument( "--drs", help="File mapping between word ids and henry literals.", type=file )
	parser.add_argument( "--target", help="Problem to be resolved (e.g. wsj_0020-000).", nargs="+" )
	parser.add_argument( "--datadir", help="Path to resources.", nargs=1 )
	parser.add_argument( "--extmod", help="Path to external module." )
	parser.add_argument( "--infmethod", help="Inference method: cpi or bnb.", default="cpi" )
	parser.add_argument( "--reasoner", help="Reasoner binary." )

	pa = parser.parse_args()

	if None == pa.reasoner:   parser.error( "Where's the reasoner?" )
	if None == pa.extmod:     parser.error( "Where's the external module?" )
	if None == pa.target:     parser.error( "Which problem should I solve?" )
	if None == pa.datadir:    parser.error( "Where's the resources?" )
	if None == pa.drs:        parser.error( "Where's the DRS file?" )
	
	for target in pa.target:
		mycoref( target, pa )
	
if "__main__" == __name__: main()
