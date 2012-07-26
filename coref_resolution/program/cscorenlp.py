
import SocketServer, socket
import argparse, re, sys
import pexpect

from lxml import etree

MSG_SHUTDOWN = "***SHUTDOWN"

class MyTCPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = ""
		
		while not data.endswith( "\n\n\n" ):
			data += self.request.recv(1024)

		if MSG_SHUTDOWN in data:
			self.request.sendall( "\n\n\n" )
			self.server.server_close()
			return
			
		for ln in data[:-3].splitlines():
			self.server.pe_corenlp.sendline( ln )
			self.server.pe_corenlp.expect( "NLP>" )
			self.request.sendall(self.server.pe_corenlp.before)

		self.request.sendall( "\n\n\n" )
			
#
# For client use.
def sendText( text, host="localhost", port=9001 ):
	sock				 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	is_data_recv = False
	
	try:
		sock.connect((host, port))
		sock.sendall(text + "\n\n\n")

		data = ""
		
		while not data.endswith( "\n\n\n" ):
			data += sock.recv(1024)

		is_data_recv = True
		
	finally:
		sock.close()

		# Convert to XML.
		xml_root		 = etree.Element( "root" )
		xml_doc			 = etree.Element( "document" ); xml_root.append( xml_doc )
		xml_sents		 = etree.Element( "sentences" ); xml_doc.append( xml_sents )
		xml_sent		 = None
		xml_toks		 = None
		xml_parse		 = None
		xml_corefset = None
		xml_dcoref	 = None
		xml_last_men = None
		
		for ln in data[:-3].splitlines():
			if "Sentence #" in ln:
				xml_sent		 = etree.Element( "sentence", attrib={"id": re.findall("#([0-9]+)", ln)[0]} ); xml_sents.append( xml_sent )
				xml_toks		 = etree.Element( "tokens" ); xml_sent.append( xml_toks )

			if "[Text=" in ln:

				mapping = { "Text": "word", "Lemma": "lemma", "PartOfSpeech": "POS", "NamedEntityTag": "NER", "NormalizedNamedEntityTag": "NormalizedNER",
										"CharacterOffsetBegin": "CharacterOffsetBegin", "CharacterOffsetEnd": "CharacterOffsetEnd" }
				
				for i, tok in enumerate( re.findall( "\[(.*?)\]", ln ) ):
					
					# Timex tag
					timex = re.findall( "Timex=.*?<\/TIMEX3>", tok )
				
					if 0 < len(timex):
						tok = tok.replace( timex[0], "" ).strip()

					def _breakIntoTuple(x):
						x = x.split("=")
						return (x[0], x[1] if 1 < len(x) else "")
					
					tok			= dict( [_breakIntoTuple(x) for x in tok.split( " " ) ] )
					xml_tok	= etree.Element( "token", attrib={"id": repr(1+i)} ); xml_toks.append( xml_tok )
					
					if 0 < len(timex):
						xml_timex = etree.Element( "Timex", attrib={"type": re.findall("type=\"(.*?)\"", timex[0])[0], "tid": re.findall("tid=\"(.*?)\"", timex[0])[0] } ); xml_tok.append( xml_timex )
						timex_val = re.findall("value=\"(.*?)\"", timex[0])

						if 0 < len(timex_val): xml_timex.text = timex_val[0]
						
					for ishell, xml_tag in mapping.iteritems():
						try:
							if tok.has_key( ishell ): xml_elem = etree.Element( xml_tag ); xml_tok.append( xml_elem ); xml_elem.text = tok[ ishell ]
						except ValueError:
							print >>sys.stderr, "Incompatible string:", tok[ ishell ]

			if ln.startswith( "Coreference set:" ):
				if None == xml_dcoref: xml_dcoref = etree.Element( "coreference" ); xml_doc.append( xml_dcoref )
				xml_corefset = etree.Element( "coreference" ); xml_dcoref.append( xml_corefset )
				xml_last_men = None

			if ", that is: " in ln:
				
				def _addMention( _ref, representative=False ):
					xml_men	= etree.Element( "mention", attrib={"representative": "True"} if representative else {}  ); xml_corefset.append( xml_men );
					xml_men_sen		= etree.Element( "sentence" ); xml_men_sen.text = _ref[0]; xml_men.append( xml_men_sen )
					xml_men_start = etree.Element( "start" ); xml_men_start.text = _ref[2]; xml_men.append( xml_men_start )
					xml_men_end		= etree.Element( "end" ); xml_men_end.text = _ref[3]; xml_men.append( xml_men_end )
					xml_men_head	= etree.Element( "head" ); xml_men_head.text = _ref[1]; xml_men.append( xml_men_head )
					return xml_men

				ref	= re.findall( "\((\d+),(\d+),\[(\d+),(\d+)\)", ln )

				if None == xml_last_men:
					xml_last_men = _addMention( ref[1], True )
					
				_addMention( ref[0] )
				
			if ln.startswith( "(ROOT" ):
				xml_parse = etree.Element( "parse" ); xml_parse.text = ln.strip(); xml_sent.append( xml_parse )
				
			if None == xml_corefset and ln.strip().startswith( "(" ):
				xml_parse.text += " " + ln.strip()

		return etree.tostring(xml_root, pretty_print=True, xml_declaration=True, encoding="utf-8") if is_data_recv else None

		
def main():
	parser = argparse.ArgumentParser( description="Client-server driver for CoreNLP." )
	parser.add_argument( "--cmd", help="Command (start, stop, or parse)." )
	parser.add_argument( "--input", help="Parsed text.", type=file, nargs="+", default=[sys.stdin] )
	parser.add_argument( "--host", help="Host to serve.", default="localhost" )
	parser.add_argument( "--port", help="Port to serve.", type=int, default=9001 )
	parser.add_argument( "--cnpath", help="Path to CoreNLP." )
	parser.add_argument( "--cnparam", help="Parameter passed to CoreNLP.", default="-annotators tokenize,ssplit" )
	pa = parser.parse_args()

	if pa.cmd not in "start stop parse".split(): parser.error( "How can I help you, sir?" )
	if "start" == pa.cmd and None == pa.cnpath:  parser.error( "Where is CoreNLP?" )

	if "start" == pa.cmd:
		classname		 = "edu.stanford.nlp.pipeline.StanfordCoreNLP"
		jars				 = ["%s/%s" % (pa.cnpath, fn) for fn in "stanford-corenlp-2012-07-09.jar:stanford-corenlp-2012-07-06-models.jar:xom.jar:joda-time.jar".split( ":" )]

		server		= SocketServer.TCPServer((pa.host, pa.port), MyTCPHandler)
		server_id = "[%s:%s]" % (pa.host, pa.port)
		cmd				= "java -cp %s -Xmx3g %s %s" % (":".join(jars), classname, pa.cnparam)
		
		print server_id, "Loading CoreNLP... (command: %s)" % cmd
		server.pe_corenlp = pexpect.spawn( cmd )
		server.pe_corenlp.expect( "NLP>" )

		print server_id, "CoreNLP loaded."

		try:
			server.serve_forever()

		except:
			print server_id, "Shutting down server..."
			server.shutdown()
			server.pe_corenlp.close()

			
	elif "stop" == pa.cmd:
		if None == sendText( MSG_SHUTDOWN + "\n\n\n", pa.host, pa.port ):
			print "Server seems not working on %s:%s." % (pa.host, pa.port)

			
	elif "parse" == pa.cmd:
		for f in pa.input:
			print sendText( f.read(), pa.host, pa.port )

			
if __name__ == "__main__":
	main()
