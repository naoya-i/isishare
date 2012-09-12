
from lxml import etree
from collections import defaultdict

import argparse, sys, os, re


def mycoref( target, pa ):

	facts	 = []
	ninput = open( pa.input[0] ).read()
	
	# Load mapping b/w entity variables and word id.
	map_var_wordid = defaultdict(list)
	mapper				 = lambda m: re.findall( "\((%s) ([^()]+) :[^:]+:[^:]+:\[([0-9ID,-]+)\]\)" % m, ninput )

	for predicate, variables, wordids in mapper("[^( ]+"): #mapper( "[^) ]+-nn" ) + mapper( "[^) ]+-vb" ) + mapper("male|neuter|female|thing"):
		for wordid in wordids.split(" "):
			wordid_conv = wordid if "ID" not in wordid else repr(int(wordid.split("-ID")[0])*1000+int(wordid.split("-ID")[1]))
			map_var_wordid[variables.split(" ")[0] if "-vb" in predicate else variables.split(" ")[1] ] += [wordid_conv]

	# List the sentences.
	xml_root	 = etree.Element("coreference-result", attrib={"text": target, "sentence": pa.sentence[0]})
	chain_id	 = 0
	hypothesis = ""
	
	try:
		if None == re.search( "\(name %s\)" % pa.sentence[0], ninput, flags=re.MULTILINE ):
			print >>sys.stderr, "No sentence found:", pa.sentence[0]
		else:

			cmd = "%s -m infer -b %s/kb-wnfn.da %s %s -d %d -p %s -t 8 -i %s -e %s -f '%s' -T %s" % (
					pa.reasoner, pa.datadir, " ".join(pa.anythingelse), pa.input[0], pa.depth,
					pa.sentence[0], pa.infmethod, pa.extmod, pa.extcmd, pa.timeout)
			print >>sys.stderr, cmd
			ret             = os.popen(cmd).read()
			xml_ret					= etree.fromstring( ret.replace( "&", "&amp;" ) )
			hypo            = xml_ret.xpath("/henry-output/result-inference/hypothesis")
			
			if 0 == len(hypo): print >>sys.stderr, "No hypothesis..."; return facts

			if None == hypothesis or None == hypo[0].text:
				print >>sys.stderr, "?", ret
				return []

			hypothesis			= hypo[0].text.strip()
			
			# Coreference-chains identified by unification.
			in_chain = []
			
			for lit in hypothesis.split(" ^ "):
				if "=(" in lit:
					xml_chain							 = etree.Element( "chain", attrib={"id": str(chain_id)} ); 	  xml_root.append( xml_chain )
					xml_chain_vars				 = etree.Element( "variables" ); xml_chain.append( xml_chain_vars )
					xml_chain_wordids			 = etree.Element( "wordids" );   xml_chain.append( xml_chain_wordids )
					xml_chain_vars.text    = re.findall( "=\((.*?)\)", lit )[0]
					xml_chain_wordids.text = ",".join( [ ",".join(map_var_wordid.get(x, "?")) for x in re.findall( "=\((.*?)\)", lit )[0].split(",") ] )

					in_chain += xml_chain_vars.text.split(",")
					chain_id += 1

			for lit in hypothesis.split( " ^ " ):
				if "(" not in lit: continue
				
				for term in re.findall( "\((.*?)\)", lit )[0].split(","):
					if not term.startswith("_") and term not in in_chain:
						xml_chain							 = etree.Element( "chain", attrib={"id": str(chain_id)} ); 	  xml_root.append( xml_chain )
						xml_chain_vars				 = etree.Element( "variables" ); xml_chain.append( xml_chain_vars )
						xml_chain_wordids			 = etree.Element( "wordids" );   xml_chain.append( xml_chain_wordids )
						xml_chain_vars.text    = term
						xml_chain_wordids.text = ",".join(map_var_wordid.get(term, "?"))

						in_chain += [term]
						chain_id += 1
					
			xml_root.append( xml_ret.xpath( "/henry-output" )[0] )

			print etree.tostring( xml_root, pretty_print=True )
			
	except etree.XMLSyntaxError, inst:
		print >>sys.stderr, "Parse error:", target, inst, inst.args, ret
			
	return facts



def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Input in Henry format.", nargs=1 )
	parser.add_argument( "--depth", help="Depth.", default=0, type=int )
	parser.add_argument( "--anythingelse", help="Commands passed to Henry.", default=[], nargs="+" )
	parser.add_argument( "--target", help="Problem to be resolved (e.g. wsj_0020-000).", nargs="+" )
	parser.add_argument( "--sentence", help="Sentence to be resolved (e.g. 1).", nargs=1 )
	parser.add_argument( "--datadir", help="Path to resources." )
	parser.add_argument("--sentbysent", help="Enable sentence-by-sentence processing.", action="store_true")
	parser.add_argument( "--extmod", help="Path to external module." )
	parser.add_argument( "--extcmd", help="Commands passed to external module.", default="" )
	parser.add_argument( "--infmethod", help="Inference method: cpi or bnb.", default="cpi" )
	parser.add_argument( "--timeout", help="Timeout.", default="10" )
	parser.add_argument( "--reasoner", help="Reasoner binary." )

	pa = parser.parse_args()

	if None == pa.reasoner:   parser.error( "Where's the reasoner?" )
	if None == pa.extmod:     parser.error( "Where's the external module?" )
	if None == pa.target:     parser.error( "Which problem should I solve?" )
	if None == pa.datadir:    parser.error( "Where's the resources?" )
	
	for target in pa.target:
		mycoref( target, pa )
	
if "__main__" == __name__: main()
