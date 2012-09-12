

from lxml import etree
from copy import copy
from collections import defaultdict

import argparse, sys, os, re


def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Input in corefout format.", nargs="+", type=file, default=[sys.stdin] )
	parser.add_argument( "--conllindex", help="Input in corefout format.", type=file )
	parser.add_argument( "--format", help="Input in corefout format.", default="graph" )
	pa = parser.parse_args()

	if None == pa.input:     parser.error( "Where's the input file?" )

	if None != pa.conllindex:
		mapper = dict( [(x.split()[0].split(".")[0], x.split()[1]) for x in pa.conllindex] )
	
	for f in pa.input:

		if "conll" == pa.format:
			fname     = re.findall( "annotations/(.*?).v2_auto_conll", mapper[ re.findall("[0-9a-z]+_[0-9]+", f.name)[0] ] )[0]
			
		x					= etree.parse( f )
		tokens		= defaultdict(dict)
		coref_ins = defaultdict(list)
		coref_del = defaultdict(list)
		coref_id  =	0
		
		if "conll" == pa.format:
			part = re.findall("-([0-9]{3})\.", f.name)[0]
			print "#begin document (%s); part %s" % (fname, part)
			
			for coref in x.xpath( "/root/document/coreference/coreference" ):
				coref_id += 1
				
				for m in coref.xpath( "./mention" ):
					coref_ins[ "%s-%s" % (m.xpath("sentence")[0].text, m.xpath("start")[0].text) ]            += [coref_id]
					coref_del[ "%s-%s" % (m.xpath("sentence")[0].text, repr(int(m.xpath("end")[0].text)-1)) ]	+= [coref_id]

		#print coref_del, coref_ins
		
		for sent in x.xpath( "/root/document/sentences/sentence" ):

			if "graph" == pa.format: print sent.attrib["id"] + ":",
			
			for w in sent.xpath( "./tokens/token/word" ):
				if "conll" == pa.format:
					corefm = []

					for m in coref_ins.get( "%s-%s" % (sent.attrib["id"], w.xpath( ".." )[0].attrib["id"]), [] ):
						corefm += ["(%s" % m]

					for m in coref_del.get( "%s-%s" % (sent.attrib["id"], w.xpath( ".." )[0].attrib["id"]), [] ):
						corefm += ["%s)" % m]
						
					print "%s %d %d %s - - - - - - - - - %s" % (fname, int(part), int(w.xpath( ".." )[0].attrib["id"])-1, w.text, "|".join(corefm) if 0 < len(corefm) else "-")
				
				if "graph" == pa.format: print w.text,
				tokens[ sent.attrib["id"] ][ w.xpath( ".." )[0].attrib["id"] ] = w.text
				
			if "graph" == pa.format: print
			if "conll" == pa.format: print

		if "graph" == pa.format:
			print

			for coref in x.xpath( "/root/document/coreference/coreference" ):

				if "graph" == pa.format: print "{",

				for m in coref.xpath( "./mention" ):
					if "graph" == pa.format: print "%s(%s)," % (tokens[ m.xpath("sentence")[0].text ][ m.xpath("head")[0].text ], 1000*int(m.xpath("sentence")[0].text)+int(m.xpath("head")[0].text)),

				if "graph" == pa.format: print "}"

		if "conll" == pa.format: print "#end document"
		
		
if "__main__" == __name__: main()
