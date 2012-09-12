
from lxml import etree
from copy import copy
from collections import defaultdict

import argparse, sys, os, re


def main():
	parser = argparse.ArgumentParser( description="WordNet synset annotator." )
	parser.add_argument( "--input", help="Henry format.", nargs="+", type=file, default=[sys.stdin] )
	parser.add_argument( "--wnindex", help="WordNet format.", nargs="+", type=file, default=[sys.stdin] )

	pa		 = parser.parse_args()
	wndict = {}
	
	for f in pa.wnindex:
		for ln in f:
			if ln.startswith(" "): continue
			
			ln													 = ln.strip().split( " " )
			lex, num_synsets						 = ln[0], int(ln[2])
			synsets											 = ln[:-num_synsets]
			wndict[lex.replace("_","-")] = synsets

	for f in pa.input:
		print f.name

		for ln in f:
			re.findall( "" )
		wndict["cake"]

if "__main__" == __name__: main()
