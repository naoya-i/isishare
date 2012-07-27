
from lxml import etree
from copy import copy

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
		
	except etree.XMLSyntaxError, inst:
		print >>sys.stderr, "Parsing Error:", pa.input[0].name, inst, inst.args
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

		# Load all the gold chains.
		current_stack = []
		gold_chains		= []
		system_chains = []
		
		for ln in open( mapper[ text_id ] ):
			ln	= ln.split()
			
			if len(ln) == 0:
				sent_id += 1
				continue
			
			elif ln[0] in ["#begin", "#end"]:
				continue
			
			global_id = sent_id * 1000 + int(ln[2])
			
			lnins = re.findall("\(([0-9]+)", ln[-1])
			lndel = re.findall("([0-9]+)\)", ln[-1])
			
			for n in lnins: current_stack += [n]
			gold_chains += [(global_id, copy(current_stack))]
			for n in lndel: current_stack.remove(n)
			
			if chain.has_key( global_id ):
				system_chains += [ (global_id, [chain[global_id]]) ]
			else:
				system_chains += [ (global_id, []) ]

		# # Extend the mention boundaries
		# for i in xrange( len(gold_chains) ):
		# 	print >>sys.stderr, gold_chains[i], system_chains[i]

		# 	for j in xrange( i+1, len(gold_chains) ):
		# 		if 0 == len(set(gold_chains[i][1]) & set(gold_chains[j][1])): break

		# 		print >>sys.stderr,  gold_chains[i], "==", gold_chains[j], system_chains[j]
				
		# 		if 0 < len(system_chains[j][1]):
		# 			print >>sys.stderr, "found!", i
		# 			chain[ system_chains[i][0] ] = system_chains[j][1][0]
		# 			#raw_input()
		# 			break
					
		# print >>sys.stderr, chain


		# current_stack = []
		# gold_chains		= []
		# system_chains = []
		# sent_id				= 1
		
		# for ln in open( mapper[ text_id ] ):
		# 	ln	= ln.split()
			
		# 	if len(ln) == 0:
		# 		sent_id += 1
		# 		continue
			
		# 	elif ln[0] in ["#begin", "#end"]:
		# 		continue
			
		# 	global_id = sent_id * 1000 + int(ln[2])
			
		# 	lnins = re.findall("\(([0-9]+)", ln[-1])
		# 	lndel = re.findall("([0-9]+)\)", ln[-1])
			
		# 	for n in lnins: current_stack += [n]
		# 	gold_chains += [(global_id, copy(current_stack))]
		# 	for n in lndel: current_stack.remove(n)
			
		# 	if chain.has_key( global_id ):
		# 		system_chains += [ (global_id, [chain[global_id]]) ]
		# 	else:
		# 		system_chains += [ (global_id, []) ]

		# for i in xrange( len(gold_chains) ):
		# 	print >>sys.stderr, gold_chains[i], system_chains[i]
				
		#print >>sys.stderr, gold_chains, system_chains

		sent_id = 1
		
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
