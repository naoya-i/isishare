
import argparse, sys, os, re
		
def main():
	parser = argparse.ArgumentParser( description="A converter from CoNLL dataset to candc input file." )
	parser.add_argument( "--conll-index", help="Index of CoNLL dataset.", type=file, dest="conllindex" )
	parser.add_argument( "--threshold", type=int, default=10 )

	pa = parser.parse_args()
	
	mapper = dict( [(x.split()[0].split(".")[0], x.split()[1]) for x in pa.conllindex] )

	for ln in sys.stdin:
		
		try:
			text_id, part_id = ln.strip().split( "-" )
		except ValueError:
			print >>sys.stderr, "?", patextid
			return

		current_text_id	 = ""
		sent_id					 = 1

		for ln in open( mapper[ text_id ] ):
			ln	= ln.split()

			if len(ln) == 0: sent_id += 1;    continue
			elif ln[0] in ["#begin"]: current_text_id = "-".join( re.findall("#begin document \(.*?([a-z]+_[0-9]+)\); part ([0-9]+)", " ".join(ln))[0] ); sent_id=1

			if "%s-%s" % (text_id, part_id) != current_text_id: continue
			if "#end" in ln[0]:
				if pa.threshold > sent_id:
					print text_id + "-" + part_id
				break
	
if "__main__" == __name__: main()
