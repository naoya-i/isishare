
import argparse, sys, re

def _constantify(x):
	x = x.split( " " )
	return "%s %s" % (x[0], " ".join( [v.upper() if not v.startswith("?") else v for v in x[1:]] ))


def main():
	parser = argparse.ArgumentParser( description="Ng & Mooney to Henry converter." )
	parser.add_argument( "--input", help="Lisp files to be converted.", type=file, nargs="+", default=sys.stdin )
	parser.add_argument( "--tlp", help="Top level plan info file.", type=file, nargs=1 )
	pa = parser.parse_args()

	if None == pa.tlp: parser.error( "Where is the top-level plan files?" )
	
	TopLevelPlans = re.findall("\(plan_.*? (.*?) ", pa.tlp[0].read() )

	for f in pa.input:
		train = {}

		for name_prefix, name_no, content in re.findall( "\(setf \*([tea]+)([0-9]+).*?'\((.*?)\)\)\n", f.read(), re.DOTALL ):

			lfs = re.findall( "\((.*?)\)", re.sub( "inst ([^ ]+) ([^\)]+)", "inst_\\2 \\1", content ).replace( "-", "_" ) )
			lfs = ["      (%s :10)" % _constantify(l) for l in lfs]

			if "a" == name_prefix[0]:

				# Add negative label to avoid hypothesize top-level plan literals
				for tlp in TopLevelPlans:
					if "inst_%s" % tlp not in [x.split()[0][1:] for x in lfs]:
						lfs += ["      (! (inst_%s *))" % tlp]

			lfs = "\n".join( lfs )

			if not train.has_key( name_no ): train[ name_no ] = {}

			train[ name_no ][ "gold" if "a" == name_prefix[0] else "obs" ] = name_prefix, lfs


		for problem in sorted( train, key=lambda x: int(x) ):
			print "(O (name %s%s) (label (^" % (train[problem]["obs"][0], problem)
			print "%s" % (train[problem]["gold"][1])
			print "     ) ) (^ "
			print train[problem]["obs"][1]
			print "     ) )"
			print
	
	
if "__main__" == __name__: main()
