
from lxml import etree
from copy import copy
from collections import defaultdict

import argparse, sys, os, re


def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Input in corefout format.", nargs="+", type=file, default=[sys.stdin] )
	parser.add_argument( "--conll-index", help="Index of CoNLL dataset.", type=file, dest="conllindex" )
	parser.add_argument( "--goldmention", help="Assume mentions are given.", action="store_true", default=False )

	pa = parser.parse_args()

	if None == pa.input:     parser.error( "Where's the input file?" )
	if None == pa.conllindex:  parser.error( "CoNLL directory, please." )
	if False == pa.goldmention: parser.error( "Not supported, yet." )
	
	mapper			 = dict( [(x.split()[0].split(".")[0], x.split()[1]) for x in pa.conllindex] )
	
	try:
		xml_corefout = etree.parse( pa.input[0] )
		
	except etree.XMLSyntaxError, inst:
		print >>sys.stderr, "Parsing Error:", pa.input[0].name, inst, inst.args
		return
	
	for xml_cr in xml_corefout.xpath( "/coreference-output/coreference-result" ):

		text_id = xml_cr.attrib[ "text" ].split("-")[0]

		# Load the system coref chain.
		system_chain = defaultdict(list)

		for xml_chain in xml_cr.xpath( "chain" ):
			for wordid in xml_chain.xpath( "wordids" )[0].text.split( "," ):
				system_chain[ int(wordid) if "?" != wordid else 0 ] += [xml_chain.attrib["id"]]
		
		# Load the gold coref chain.
		gold_chain		 = {}
		sent_id				 = 1
		current_stack	 = []
		system_response = {}
		
		for ln in open( mapper[ text_id ] ):
			ln	= ln.split()
			
			if len(ln) == 0: sent_id += 1;    continue
			elif ln[0] in ["#begin", "#end"]: continue
			
			global_id = sent_id * 1000 + int(ln[2])
			
			lnins = re.findall("\(([0-9]+)", ln[-1])
			lndel = re.findall("([0-9]+)\)", ln[-1])
			
			for n in lnins: current_stack += [n]
			
			if system_chain.has_key( global_id ):
				for n in current_stack:
					system_response[n] = int(system_chain[global_id][0])
																													
			for n in lndel: current_stack.remove(n)

		# Annotate.
		sent_id				= 1
		phase					= 0
		cnt						= {}
		current_stack = []
		
		for ln in open( mapper[ text_id ] ):
			ln	= ln.split()
			
			if len(ln) == 0: sent_id += 1;    continue
			elif ln[0] in ["#begin", "#end"]: print " ".join( ln ); continue
			
			global_id = sent_id * 1000 + int(ln[2])
			
			lnins = re.findall("\(([0-9]+)", ln[-1])
			lndel = re.findall("([0-9]+)\)", ln[-1])

			ln[-1] = ""
			
			for n in lnins:
				cnt[n] = 10000 + phase
				phase += 1
				if "" != ln[-1]: ln[-1] += "|"
				ln[-1] += "(%s" % system_response.get( n, cnt[n] )
			
			for n in lndel:
				if "" != ln[-1] and "(%s" % system_response.get( n, cnt[n] ) not in ln[-1]: ln[-1] += "|"
				ln[-1] += "%s)" % system_response.get( n, cnt[n] ) if "(%s" % system_response.get( n, cnt[n] ) not in ln[-1] else ")"

			if "" == ln[-1]: ln[-1] = "-"
			
			print " ".join( ln )
	
	
if "__main__" == __name__: main()
