
import argparse, sys, os, re


def mycoref( target, pa ):

	facts = []

	print os.popen( "%s -m infer %s -p %s" % ( pa.reasoner, " ".join( pa.input ), target ) ).read()

	# Reproduce the CoNLL format.

	# Load mapping b/w entity variables and word id.
	drs = pa.drs.read()
	
	print re.findall( "\[([^]]+)\]:([^(]+-n)\(.*?,(.*?)\)", drs ) + re.findall( "\[([^]]+)\]:([^(]+-v)\((.*?),", drs )
	
	return facts



def main():
	parser = argparse.ArgumentParser( description="Abductive coreference resolution system." )
	parser.add_argument( "--input", help="Henry format.", nargs="+" )
	parser.add_argument( "--drs", help="File mapping between word ids and henry literals.", type=file )
	parser.add_argument( "--target", help="Problem to be resolved (e.g. wsj_0020-000).", nargs="+" )
	parser.add_argument( "--reasoner", help="Reasoner binary." )

	pa = parser.parse_args()

	if None == pa.reasoner: parser.error( "Where's the reasoner?" )
	if None == pa.target:   parser.error( "Which problem should I solve?" )
	if None == pa.drs:      parser.error( "Where's the DRS file?" )
	
	for target in pa.target:
		mycoref( target, pa )
	
if "__main__" == __name__: main()
