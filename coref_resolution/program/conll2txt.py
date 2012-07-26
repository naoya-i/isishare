
import argparse, sys, os, re


def conll2raw( txt, pa ):
	for i, ln in enumerate( txt.strip().split( "\n" ) ):
		if "" == ln or ("raw" == pa.format and "#begin" in ln or "#end" in ln): continue

		if "raw" == pa.format:
			ln = ln.split()
			print ln[3],
			
		else:
			print ln.strip()
	
		
def main():
	parser = argparse.ArgumentParser( description="A converter from CoNLL dataset to candc input file." )
	parser.add_argument( "--input", help="CoNLL file (s).", nargs="+", default=["-"] )
	parser.add_argument( "--textid", help="Text ID (e.g. wsj_0030-000)." )
	parser.add_argument( "--format", help="Destination format (raw, or conll).", default="raw" )

	pa = parser.parse_args()

	if None == pa.textid:          parser.error( ":(" )
	if None == re.match( "[a-z]+_[0-9]{4}-[0-9]{3}$", pa.textid ): parser.error( "Invalid text ID format (e.g. wsj_0030-000)." )
	
	buf			 = None
	num_conv = 0

	for f in pa.input:
		num_conv += 1
		print >>sys.stderr, "%4d/%4d:" % (num_conv, len(pa.input)), f
		
		for ln in (open(f) if "-" != f else sys.stdin):
			if "begin document" in ln:
				doc, prt = re.findall( "^#begin document \((.*?)\); part ([0-9]+)", ln )[0]
				buf			 = ln if "%s-%s" % (doc.split("/")[-1], prt) == pa.textid else None
				
			elif None != buf:
				if "end document" in ln: buf += ln; conll2raw( buf, pa ); buf = ""
				else:                    buf += ln
	
	
if "__main__" == __name__: main()
