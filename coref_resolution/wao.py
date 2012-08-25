import sys, re

def m(x):
	if x.group(1) == x.group(2): return "(%s)" % x.group(1)
	return x.group(0)
	
for ln in sys.stdin:
	ln = re.sub( "\(([0-9]+)\|([0-9]+)\)", m, ln )
	print ln.strip()
