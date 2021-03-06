
import sys, re

# Usage:
#  python henry2n700.py <input_file> <input_file> ...

def se(x):
	x = x.strip()
	if "!=" not in x:
		pred, args, cost, name = re.findall( "(.*?)\((.*?)\):(.*?):(.*?)", x )[0]
		args = args.split(",")
	else:
		args = re.findall( "(.+)!=(.+)", x )[0]
		pred = "!="
		
	return "(%s %s)" % (pred, " ".join( args ) )


def se2(x):
	x = x.strip()
	cost = ""
	if "!=" not in x:
		xx = re.findall( "(.*?)\((.*?)\):([.0-9]+)", x )
		if 0 != len(xx):
			pred, args, cost = xx[0]
		else:
			xx = re.findall( "(.*?)\((.*?)\)", x )[0]
			
			if 0 != len(xx):
				pred, args = xx
			else:
				return ""
			
		args = args.split(",")
	else:
		args = re.findall( "(.+) != (.+)", x )[0]
		pred = "!="

	return "(%s %s)" % (pred, " ".join( args )) if "" == cost else \
			"(%s %s :%s)" % (pred, " ".join( args ), cost)



hosh = {}

for fn in sys.argv[1:]:
	for ln in open(fn):
		ln = ln.strip().replace( "'", "" ).replace( ";", "\\;" )

		lnx = re.findall( "(.*?)] (.*)", ln )
		if 0 == len(lnx): continue

		obs, lit = lnx[0]

		if "=>" in ln:
			lit = lit.split( " => " )
			if 2 != len(lit): print >>sys.stderr, "?:", lit; continue

			weights = re.findall( ":([0-9.]+)", lit[0] )
				
			print "(B (name %s) (=> (^ %s) (^ %s) ) )" % (obs,
																					 " ".join( [se2(x) for x in lit[0].split( " & " )]),
																					 " ".join( [se2(x) for x in lit[1].split( " & " )]) )
			
		else:
			print "(O (name %s) (^ %s) )" % (obs, " ".join( [se(x) for x in lit.split( " & " )]))
	
for k, v in hosh.iteritems():
	print v
