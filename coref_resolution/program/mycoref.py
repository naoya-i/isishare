
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
	
	for obs_sent in re.findall( "(%s_[0-9]+)\]" % target, henry ):
		xml_coreference = etree.Element( "coreference-output" )
		xml_ret					= etree.parse( os.popen( "%s -m infer %s -d 2 -p %s -b %s/kb.da -i cpi" % ( pa.reasoner, pa.input[0], obs_sent, pa.datadir[0] ) ) )
		hypothesis			= xml_ret.xpath( "/henry-output/result-inference/hypothesis" )[0].text
		
		for lit in hypothesis.split( " ^ " ):			
			if "=(" in lit:
				xml_chain							 = etree.Element( "chain" ); 	  xml_coreference.append( xml_chain )
				xml_chain_vars				 = etree.Element( "variables" ); xml_chain.append( xml_chain_vars )
				xml_chain_wordids			 = etree.Element( "wordids" );   xml_chain.append( xml_chain_wordids )
				xml_chain_vars.text    = re.findall( "=\((.*?)\)", lit )[0]
				xml_chain_wordids.text = ",".join( [ "/".join(map_var_wordid.get(x, "?")) for x in re.findall( "=\((.*?)\)", lit )[0].split(",") ] )

		xml_root.append( xml_ret.xpath( "/henry-output" )[0] )
		xml_root.append( xml_coreference )
		
	print etree.tostring( xml_root, pretty_print=True )
			
	return facts



def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Input in Henry format.", nargs=1 )
	parser.add_argument( "--henry", help="File mapping between word ids and henry literals.", nargs=1 )
	parser.add_argument( "--drs", help="File mapping between word ids and henry literals.", type=file )
	parser.add_argument( "--target", help="Problem to be resolved (e.g. wsj_0020-000).", nargs="+" )
	parser.add_argument( "--datadir", help="Path to resources.", nargs=1 )
	parser.add_argument( "--reasoner", help="Reasoner binary." )

	pa = parser.parse_args()

	if None == pa.reasoner:  parser.error( "Where's the reasoner?" )
	if None == pa.target:    parser.error( "Which problem should I solve?" )
	if None == pa.datadir:   parser.error( "Where's the resources?" )
	if None == pa.drs:       parser.error( "Where's the DRS file?" )
	
	for target in pa.target:
		mycoref( target, pa )
	
if "__main__" == __name__: main()
