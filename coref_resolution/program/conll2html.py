
from lxml import etree
from StringIO import StringIO

import argparse
import sys, re, collections


def main():
	parser = argparse.ArgumentParser( description="CoNLL data visualizer." )
	parser.add_argument( "--input", help="CoNLL data to be visualized.", nargs="+", default=[sys.stdin], type=file )
	parser.add_argument( "--gold", help="CoNLL gold data to be visualized.", nargs="+", type=file )
	parser.add_argument( "--coref", help="CoNLL coreference data to be visualized.", nargs="+", type=file )
	pa = parser.parse_args()

	if None == pa.input: parser.error( "CoNLL file, please." )

	xmldic	= {}
	golddic	= {}

	if None != pa.coref:
		for f in pa.coref:
			x = etree.parse(f)

			try:
				xmldic[ x.xpath( "/coreference-output/coreference-result" )[0].attrib["text"] ] = x

			except IndexError:
				print >>sys.stderr, "?"

	if None != pa.gold:
		for fs in pa.gold:
			x															= fs.readlines()
			ti														= re.findall( "/([a-z]+_[0-9]+)", x[0] )[0]
			pn														= re.findall( "part ([0-9]+)", x[0] )[0]
			golddic[ "%s-%s" % (ti, pn) ] = x

			
	startPrettyPrint()
	
	for fs in pa.input:
		
		# Read two mappings from the file: Word ID->word, and Word ID->coref chain.
		for prt, words, corefmap in read( fs ):

			ti = re.findall( "([a-z]+_[0-9]+)", fs.name )[0]
			pn = re.findall( "part ([0-9]+)", prt )[0]

			if golddic.has_key("%s-%s" % (ti, pn)): 
				g	 = [x for x in read( StringIO("\n".join(golddic["%s-%s" % (ti, pn)]) ) )]
			else:
				g = []

			corefmap = dict( [(x, ["S%d" % z for z in y]) for x, y in corefmap.iteritems()] )

			if 0 < len(g):
				for gcm in g[0][2].iteritems():
					corefmap[ gcm[0] ] += ["G%d" % z for z in gcm[1]]
				
			# Output them in HTML format.
			prettyPrint( words, corefmap, "%s - %s" % (fs.name, prt) )

			try:
				print "<br />"

				if None != pa.coref:
					print "<code>Best vector: <br /> %s</code>" % xmldic["%s-%s" % (ti, pn)].xpath( "/coreference-output/coreference-result/henry-output/result-inference/vector" )[0].text

			except IndexError:
				print "No vector"

			print "<hr />"
				
	endPrettyPrint()

def startPrettyPrint():
	print """
	<html>
	<head>
	<script type="text/javascript">
	var g_current_hilights = new Array();
	function _lightup(n, f_clear) {
		var es = document.getElementsByName('c' + n);
		if(f_clear) {
      for(var i=0;i<g_current_hilights.length;i++)
			  g_current_hilights[i].style.background = '';
      g_current_hilights = new Array();
    }
    var color = g_current_hilights.length > 0 ? '#ffcccc' : 'yellow';
		for(var i=0;i<es.length;i++) {
			es[i].style.background = color;
		  g_current_hilights.push( es[i] );
    }
	}
	</script></head>
	<body style="font-size: 1.1em; line-height: 1.3em">
	"""

def endPrettyPrint():
	print "</body></html>"
	
def read( s ):
	
	# Stack for coreference chain
	doc = ""
	i		= 0
	
	for ln in s:
		ln = ln.strip()

		if "#end" in ln: yield doc, words, corefmap
		
		if "#begin" in ln:
			doc			 = ln[ len( "#begin document " ): ]
			words    = {}
			corefmap = collections.defaultdict( list )
			nstack	 = []
			sent_id  = 0
			
		if "" == ln or ln.startswith("#"): sent_id+=1; continue

		ln = re.split( "[ ]+", ln.strip() )

		words[i]		= (sent_id, ln[3])
		corefmap[i] = []

		# If there is any coreference information,
		stacker, popper = [], []
		
		if "-" != ln[-1]:
			# Stack it, or pop it up.
			stacker = re.findall( "\(([0-9]+)", ln[-1] )
			popper  = re.findall( "([0-9]+)\)", ln[-1] )

		for n in stacker: nstack += [ int(n) ]
		for n in nstack:  corefmap[ i ] += [n] if int(n) < 10000 else []
		for n in popper:  nstack.remove( int(n) )

		
		i += 1


def prettyPrint( words, corefmap, title="" ):
	
	nstack = []

	if "" != title:
		print "<h3>-- %s</h3>" % title

	print "<div style=\"background-color:#cccccc\">"

	prev_sid = -1
	
	for i, w in words.iteritems():

		if -1 == prev_sid: prev_sid = w[0]; print "<b>%s:</b>" % w[0],
		if w[0] != prev_sid: print "<br />"; print "<b>%s:</b>" % w[0],

		prev_sid = w[0]
		
		kill				= {}

		# Need to close the current mention area?
		for n in reversed(nstack):
			if n not in corefmap[i]:
				sys.stdout.write( "]</span><sub><span style=\"cursor:pointer;\" onclick=\"_lightup('%s', !event.altKey); event.cancelBubble=true;\"><font color=\"blue\" size=\"2.0em\">%s</font></span></sub>" % (n, n) )
				kill[n] = 1

		print

		# Need to start new mention?
		for n in corefmap[i]:
			if n not in nstack:
				sys.stdout.write( "<span name=\"c%s\" style=\"color:gray;\">[" % n )
				nstack += [n]

		for n in kill:
			nstack.remove(n)

		# Wordy!
		sys.stdout.write( w[1] )

	print "</div>"

if "__main__" == __name__: main()
