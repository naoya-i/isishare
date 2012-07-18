
import argparse, sys, os, re

def main():
	parser = argparse.ArgumentParser( description="candc chopper. Break into single sentences." )
	parser.add_argument( "--input", help="ccg file.", nargs="+", type=file, default=[sys.stdin] )
	pa = parser.parse_args()

	for f in pa.input:
		the_ccg		= f.read()
		sent2text = {}
		
		for text_id, sentence_ids in re.findall( "id\( '(.*?)', \[(.*?)\]\)\.", the_ccg ):
			sent2text.update( dict( [(x, text_id) for x in sentence_ids.split( ", " )] ) )

		the_ccg = re.sub( "id\( '(.*?)', \[(.*?)\]\)\.", "", the_ccg )
			
		def _replacer(x):
			return "id( '%s_%s', [%s] ).\n\nccg(%s," % (sent2text[ x.group(1) ], x.group(1), x.group(1), x.group(1))
		
		print re.sub( "ccg\(([0-9]+),", _replacer, the_ccg )

if "__main__" == __name__: main()
