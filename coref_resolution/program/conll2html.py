
import sys, re, collections

# Usage:
#  python conll2011viscoref.py <input_file1> <input_file2> ...

def main():

	startPrettyPrint()
	
	for fn in sys.argv[1:]:
		
		# Read two mappings from the file: Word ID->word, and Word ID->coref chain.
		words, corefmap = read( open(fn) )

		# Output them in HTML format.
		prettyPrint( words, corefmap, fn )

	endPrettyPrint()

def startPrettyPrint():
	print """
	<html>
	<head>
	<script type="text/javascript">
	var g_current_hilights = new Array();
	function _lightup(n) {
		var es = document.getElementsByName('c' + n);
		for(var i=0;i<g_current_hilights.length;i++)
			g_current_hilights[i].style.color = 'gray';
		for(var i=0;i<es.length;i++)
			es[i].style.color = 'red';
		g_current_hilights = es; 
	}
	</script></head>
	<body style="font-size: 1.1em; line-height: 1.3em">
	"""

def endPrettyPrint():
	print "</body></html>"
	
def read( s ):
	
	# Unique ID to word mapping
	# Unique ID to coreference chain ID mapping
	words    = {}
	corefmap = collections.defaultdict( list )
	
	# Stack for coreference chain
	nstack   = []
	
	for i, ln in enumerate( s ):
		ln = ln.strip()

		if "" == ln or ln.startswith("#"): continue

		ln = re.split( "[ ]+", ln.strip() )

		words[i] = ln[3]

		# If there is any coreference information,
		stacker, popper = [], []
		
		if "-" != ln[-1]:
			# Stack it, or pop it up.
			stacker = re.findall( "\(([0-9]+)", ln[-1] )
			popper  = re.findall( "([0-9]+)\)", ln[-1] )

		for n in stacker:
			nstack += [ int(n) ]

		for n in nstack:
			corefmap[ i ] += [n]

		for n in popper:
			nstack.remove( int(n) )

	return words, corefmap


def prettyPrint( words, corefmap, title="" ):
	
	nstack = []

	if "" != title:
		print "<h3>-- %s</h3>" % title
		
	for i, w in words.iteritems():

		kill = {}

		# Need to close the current mention area?
		for n in nstack:
			if n not in corefmap[i]:
				sys.stdout.write( "</span>]<sub><font color=\"gray\">%d</font></sub>" % n )
				kill[n] = 1

		print

		# Need to start new mention?
		for n in corefmap[i]:
			if n not in nstack:
				sys.stdout.write( "[<span name=\"c%d\" style=\"color:gray;\" onclick=\"_lightup(%d); event.cancelBubble=true;\">" % (n, n) )
				nstack += [n]

		for n in kill:
			nstack.remove(n)

		# Wordy!
		sys.stdout.write( w )

	print "<hr />"

if "__main__" == __name__: main()
