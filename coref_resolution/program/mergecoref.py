

from lxml import etree

import argparse, sys, os, re


def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Input in corefout format.", nargs="+", type=file, default=[sys.stdin] )
	parser.add_argument( "--conll-index", help="Index of CoNLL dataset.", type=file, dest="conllindex" )
	parser.add_argument( "--gold-mention", help="Assume mention boundary is given.", action="store_true", default=False )

	pa = parser.parse_args()

	if None == pa.input:     parser.error( "Where's the input file?" )
	if None == pa.conllindex:  parser.error( "CoNLL directory, please." )

	mapper			 = dict( [(x.split()[0].split(".")[0], x.split()[1]) for x in pa.conllindex] )
	xml_corefout = etree.parse( pa.input[0] )
	
	for xml_cr in xml_corefout.xpath( "/coreference-output/coreference-result" ):

		# Load the coref chain in it.
		chain = {}
		
		for xml_chain in xml_cr.xpath( "chain" ):
			chain = dict( [(int(wordid) if "?" != wordid else 0, xml_chain.attrib["id"]) for wordid in xml_chain.xpath( "wordids" )[0].text.split( "," )] )

		sent_id = 1
		
		for ln in open( mapper[ xml_cr.attrib[ "text" ].split("-")[0] ] ):
			ln = ln.split()
			
			if len(ln) == 0:
				sent_id += 1
			elif ln[0] in ["#begin", "#end"]:
				pass
			else:
				ln[-1] = "-"
				
				if chain.has_key( sent_id * 1000 + int(ln[2]) ):
					ln[-1] = "(%s)" % chain[ sent_id * 1000 + int(ln[2]) ]
			
			print "\t".join( ln )
	
	
if "__main__" == __name__: main()
