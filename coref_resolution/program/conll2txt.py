
import argparse, sys, os, re

from lxml import etree

def conll2raw( txt, pa, adjust ):

	word_id			= 0
	out_word_id = 0
	
	for i, ln in enumerate( txt.strip().split( "\n" ) ):
		if "raw" == pa.format and ("#begin" in ln or "#end" in ln): continue
		if "" == ln:
			print
			continue

		if "raw" == pa.format:
			ln = ln.split()
			print ln[3], 
			
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
	parser.add_argument( "--format", help="Destination format (raw, or conll).", default="raw" )

	pa = parser.parse_args()

	if None == pa.textid:          parser.error( ":(" )
	if None == re.match( "[a-z]+_[0-9]{4}-[0-9]{3}$", pa.textid ): parser.error( "Invalid text ID format (e.g. wsj_0030-000)." )
	
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
