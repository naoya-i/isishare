
import sys
import argparse, sys, os, re

def main():
	parser = argparse.ArgumentParser( description="DRS id shifter." )
	parser.add_argument( "--input", help="DRS file.", nargs="+", type=file, default=[sys.stdin] )
	parser.add_argument( "--baseid", help="Base ID.", type=int )

	pa = parser.parse_args()

	if None == pa.input:       parser.error( "Where's the DRS file?" )
	if None == pa.baseid:      parser.error( "Where's the base ID?" )

	for f in pa.input:
		for ln in f:
			ln = ln.rstrip()

			ln = re.sub( "^id\((.*?),([0-9]+)\)", lambda m: "id(%s,%d)" % (m.group(1), 1+int(m.group(2))-pa.baseid/1000), ln )
			ln = re.sub( "^([0-9]+) ", lambda m: "%d " % (int(m.group(1)) - pa.baseid+1000), ln )
			ln = re.sub( "\[([0-9,]+)\]:", lambda m: "[%s]:" % ",".join([str(int(x) - pa.baseid+1000) for x in m.group(1).split(",")]), ln )

			print ln
	
	
if "__main__" == __name__: main()

