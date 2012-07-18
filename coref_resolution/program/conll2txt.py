
import argparse, sys, os, re


def conll2raw( txt ):
	for ln in txt.split( "\n" ):
		if "" == ln or "#begin" in ln or "#end" in ln: continue
		ln = ln.split()

		if "0" == ln[2]: print
		
		print ln[3],

		
def conll2candc( txt ):
	doc, prt = re.findall( "^#begin document \((.*?)\); part ([0-9]+)", txt )[0]
	snt_id	 = 0

	print "\n<META> '%s-%s'" % (os.path.basename(doc), prt)
	
	for ln in txt.split( "\n" ):
		if "" == ln or "#begin" in ln or "#end" in ln: continue
		ln = ln.split()
		
		if "0" == ln[2]: print
		
		print ln[3],

		
def main():
	parser = argparse.ArgumentParser( description="A converter from CoNLL dataset to candc input file." )
	parser.add_argument( "--input", help="CoNLL file(s).", nargs="+" )
	parser.add_argument( "--format", help="Output format.", default="raw" )

	pa = parser.parse_args()

	if None == pa.input:       parser.error( ":(" )
	
	if "raw" == pa.format:     converter = conll2raw
	elif "candc" == pa.format: converter = conll2candc

	buf			 = ""
	num_conv = 0

	for f in pa.input:
		num_conv += 1
		print >>sys.stderr, "%4d/%4d:" % (num_conv, len(pa.input)), f
		
		for ln in open(f):
			if "begin document" in ln: buf = ln
			elif "end document" in ln: buf += ln; converter( buf ); buf = ""
			else:                      buf += ln
	
	
if "__main__" == __name__: main()
