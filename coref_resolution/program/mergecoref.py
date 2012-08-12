
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
	
	mapper = dict( [(x.split()[0].split(".")[0], x.split()[1]) for x in pa.conllindex] )
	
	try:
		xml_corefout = etree.parse( pa.input[0] )
		
	except etree.XMLSyntaxError, inst:
		print >>sys.stderr, "Parsing Error:", pa.input[0].name, inst, inst.args
		return
	
	for xml_cr in xml_corefout.xpath( "/coreference-output/coreference-result" ):

		text_id, part_id = xml_cr.attrib[ "text" ].split("-")

		# Load the system coref chain.
		system_chain = defaultdict(list)

		for xml_chain in xml_cr.xpath( "chain" ):
			if 1 == len(set(xml_chain.xpath( "wordids" )[0].text.split( "," ))): continue

			for wordid in xml_chain.xpath( "wordids" )[0].text.split( "," ):
				#print >>sys.stderr, wordid, xml_chain.attrib["id"]
				system_chain[ int(wordid) if "?" != wordid else 0 ] += [xml_chain.attrib["id"]]
		
		# Load the gold coref chain.
		gold_chain			= {}
		sent_id					= 1
		current_stack		= []
		system_response = defaultdict(dict)
		cnt_m           = defaultdict(int)

		#print >>sys.stderr, system_chain
		
		for ln in open( mapper[ text_id ] ):
			ln	= ln.split()
			
			if len(ln) == 0: sent_id += 1;    continue
			elif ln[0] in ["#begin", "#end"]: sent_id=1; continue
			
			global_id = sent_id * 1000 + int(ln[2]) + 1
			
			lnins = re.findall("\(([0-9]+)", ln[-1])
			lndel = re.findall("([0-9]+)\)", ln[-1])
			
			for n in lnins:
				current_stack += [n]
				cnt_m[n] += 1
				#print >>sys.stderr, n, global_id, ln[3]
			
			if system_chain.has_key( global_id ):
				for n in current_stack:
					#print >>sys.stderr, n, ln[3]
					system_response["%s-%s" % (n, cnt_m[n])] = int(system_chain[global_id][0])
					
			for n in lndel: current_stack.remove(n)

		# Annotate.
		sent_id					= 1
		current_text_id = ""
		phase						= 0
		cnt							= {}
		ref_cnt					= defaultdict(int)
		current_stack		= []
		refm						= defaultdict(list)
		cnt_m           = defaultdict(int)
		
		for ln in open( mapper[ text_id ] ):
			ln	= ln.split()
			
			if len(ln) == 0:
				sent_id += 1
				if "%s-%s" % (text_id, part_id) == current_text_id: print
				continue
			
			if ln[0] in ["#begin"]: current_text_id = "-".join( re.findall("#begin document \(.*?([a-z]+_[0-9]+)\); part ([0-9]+)", " ".join(ln))[0] ); sent_id=1

			if "%s-%s" % (text_id, part_id) != current_text_id: continue
			if ln[0] in ["#begin", "#end"]: print " ".join( ln ); continue
			
			global_id = sent_id * 1000 + int(ln[2]) + 1
			
			lnins = re.findall("\(([0-9]+)", ln[-1])
			lndel = re.findall("([0-9]+)\)", ln[-1])

			ln[-1] = ""
			
			for n in lnins:
				if not cnt.has_key(n):
					cnt[n] = 100000 + phase

				cnt_m[n] += 1
				ref_cnt[n] += 1
				phase += 1

				# if not system_response.has_key( "%s-%s" % (n, cnt_m[n]) ):
				# 	refm[n] += [-1]
				# 	continue
				
				#print >>sys.stderr, n, global_id
				
				if "" != ln[-1]: ln[-1] += "|"

				ln[-1] += "(%s" % system_response.get( "%s-%s" % (n, cnt_m[n]), cnt[n] )
				refm[n] += [system_response.get( "%s-%s" % (n, cnt_m[n]), cnt[n] )]

			for n in lndel:
				got_cha = refm[n].pop()

				if -1 == got_cha: continue
				
				f_already_annotated = repr(got_cha) in ln[-1].split( "(" )
				if "" != ln[-1] and not f_already_annotated: ln[-1] += "|"
				ln[-1] += "%s)" % got_cha if not f_already_annotated else ")"

				ref_cnt[n] -= 1

				if 0 == ref_cnt[n]: del cnt[n]

			if "" == ln[-1]: ln[-1] = "-"

			print " ".join( ln )
	
	
if "__main__" == __name__: main()
