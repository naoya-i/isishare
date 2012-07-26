
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

	try:
		xml_corefout = etree.parse( pa.input[0] )
		
	except etree.XMLSyntaxError:
		print >>sys.stderr, "Parsing Error:", pa.input[0]
		return
	
	for xml_cr in xml_corefout.xpath( "/coreference-output/coreference-result" ):

		# Load the coref chain in it.
		chain = {}
		
		for xml_chain in xml_cr.xpath( "chain" ):
			chain.update( dict( [(int(wordid) if "?" != wordid else 0, xml_chain.attrib["id"]) for wordid in xml_chain.xpath( "wordids" )[0].text.split( "," )] ) )

		print >>sys.stderr, chain
		
		sent_id = 1
		text_id  = xml_cr.attrib[ "text" ].split("-")[0]

		if not mapper.has_key( text_id ):
			print >>sys.stderr, "Error:", text_id
			continue
		
		for ln in open( mapper[ text_id ] ):
			ln = ln.split()
			
			if len(ln) == 0:
				sent_id += 1
			elif ln[0] in ["#begin", "#end"]:
				pass
			else:
				ln[-1]		= "-"
				global_id = sent_id * 1000 + int(ln[2])
				
				if chain.has_key( global_id ):
					if chain.get( global_id-1 ) != chain[ global_id ]: ln[-1] = "(%s" % chain[ global_id ]
					if chain.get( global_id+1 ) != chain[ global_id ]:
						if "-" == ln[-1]: ln[-1] = "%s)" % chain[ global_id ]
						else:             ln[-1] += ")"
					

			#print sent_id
			print " ".join( ln )
	
	
if "__main__" == __name__: main()
