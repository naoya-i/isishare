
import argparse, sys, os, re

from collections import defaultdict
from lxml import etree

def _getFirstRightMostNN( words ):
	n = -1

	for i, w in enumerate(words):
		if w[4].startswith( "NN" ): n = i
		elif -1 != n:               break

	return n

	
def _getHead( words ):
	#print >>sys.stderr, words[0][5], " ".join( [w[4] for w in words] ), " ".join( [w[3] for w in words] ), _getFirstRightMostNN( words )
	return words[ _getFirstRightMostNN( words ) ][2]


def conll2raw( txt, pa, adjust ):

	sent_id     = 1
	word_id			= 0
	out_word_id = 0
	coref_chain = defaultdict(list)
	ln_buffer		= []
	
	for i, ln in enumerate( txt.strip().split( "\n" ) ):
		if "xml" == pa.format and "#begin" in ln:
			print """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<root>
 <document>
  <sentences>"""
			continue

		if "xml" == pa.format and "#end" in ln:

			print "  </tokens></sentence></sentences>"
			
			print "  <coreference>"

			for mentions in coref_chain.values():
				print "   <coreference>"

				for sid, tstart, tend, head in mentions:
					print """    <mention>
     <sentence>%s</sentence>
     <start>%s</start>
     <end>%s</end>
     <head>%s</head>
    </mention>""" % (sid, tstart, tend+1 if -1 != tend else tstart+1, head if -1 != tend else tstart)
					
				print "   </coreference>"
			
			print "  </coreference>"
			
			print """ </document>
</root>"""
			continue
		
		if "raw" == pa.format and ("#begin" in ln or "#end" in ln): continue
		
		if "" == ln:
			ln_buffer = []
			
			if "xml" == pa.format:
				sent_id += 1
			else:
				print
				
			continue

		if "raw" == pa.format:
			ln = ln.split()
			print ln[3], 

		elif "xml" == pa.format:
			ln = ln.split()

			ln_buffer += [ln]

			if "0" == ln[2]:
				if sent_id > 1: print "   </tokens></sentence>"
				print "   <sentence id=\"%s\"><tokens>" % (sent_id)

			ew = etree.Element("word");  ew.text=unicode(ln[3])
			el = etree.Element("lemma"); el.text=unicode(ln[6] if "-" != ln[6] else ln[3])
			
			print """    <token id="%d">
     %s
     %s
     <CharacterOffsetBegin>%s</CharacterOffsetBegin>
     <CharacterOffsetEnd>%s</CharacterOffsetEnd>
     <POS>%s</POS>
     <NER>%s</NER>
    </token>""" % (1+int(ln[2]),
									 etree.tostring(ew), etree.tostring(el),
									 0, 0, ln[4], ln[10])

			lnins		 = re.findall("\(([0-9]+)[ |]", ln[-1] + " ")
			lninsSng = re.findall("\(([0-9]+)\)", ln[-1])
			lndel		 = re.findall("[ |]([0-9]+)\)", " " + ln[-1])

			for ch in lnins:
				coref_chain[ch] += [[sent_id, 1+int(ln[2]), -1, -1]]
				
			for ch in lndel:
				coref_chain[ch][-1][2] = 1+int(ln[2])
				coref_chain[ch][-1][3] = 1+int(_getHead( ln_buffer[coref_chain[ch][-1][1]-1:int(ln[2])+1] ))

			for ch in lninsSng:
				coref_chain[ch] = [[sent_id, 1+int(ln[2]), 1+int(ln[2]), 1+int(ln[2])]] + coref_chain[ch]

				
		else:
			
			if "#begin" not in ln and "#end" not in ln:

				print ln.strip()
				# ln = ln.split()

				# ln[2] = repr(out_word_id)
				
				# print " ".join(ln)

				# print adjust[word_id]
				# word_id += 1
				# out_word_id += 1

				# if "." == adjust[word_id-1][2]:
				# 	print
				# 	out_word_id = 0
					
				# #if "." == ln[4] and "1" != adjust[word_id][1]:
				# 	# print "A:", adjust[word_id]
				# 	# out_word_id = 0
				# 	# word_id += 1
				# 	# print

			else:
				print ln.strip()
				
		
def main():
	parser = argparse.ArgumentParser( description="A converter from CoNLL dataset to candc input file." )
	parser.add_argument( "--input", help="CoNLL file (s).", nargs="+", default=["-"] )
	parser.add_argument( "--adjust", help="CoreNLP file (s).", type=file )
	parser.add_argument( "--textid", help="Text ID (e.g. wsj_0030-000)." )
	parser.add_argument( "--format", help="Destination format (raw, xml, or conll).", default="raw" )

	pa = parser.parse_args()

	if None == pa.textid:          parser.error( ":(" )
	if None == re.match( "[a-z0-9]+_[0-9]{4}-[0-9]{3}$", pa.textid ): parser.error( "Invalid text ID format (e.g. wsj_0030-000)." )
	
	buf			 = None
	num_conv = 0
	adjust   = []
	
	if None != pa.adjust:
		x	= etree.parse( pa.adjust )
		for w in x.xpath( "/root/document/sentences/sentence/tokens/token" ):
			adjust += [(w.xpath( "../.." )[0].attrib["id"], w.attrib["id"], w.xpath("word")[0].text)]

	#print adjust
	
	for f in pa.input:
		num_conv += 1
		print >>sys.stderr, "%4d/%4d:" % (num_conv, len(pa.input)), f
		
		for ln in (open(f) if "-" != f else sys.stdin):
			if "begin document" in ln:
				doc, prt = re.findall( "^#begin document \((.*?)\); part ([0-9]+)", ln )[0]
				buf			 = ln if "%s-%s" % (doc.split("/")[-1], prt) == pa.textid else None
				#if "raw" != pa.format: #print ln.strip()
				
			elif None != buf:
				if "end document" in ln:
					buf += ln; conll2raw( buf, pa, adjust ); buf = ""
				else:                    buf += ln
	
	
if "__main__" == __name__: main()
