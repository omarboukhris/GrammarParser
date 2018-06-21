from parselib.grammarparser		import *
from parselib.parsers			import *
from parselib.generaloperators	import *
from parselib.normoperators		import *

import sys

source = """
class myclass {
 public int c ;
} ;
"""

if __name__ == '__main__':
	
	fstream = open ("grammar.grm", "r")
	#fstream = open ("expgrammar.grm", "r")
	txtgrammar = "".join(fstream.readlines())
	fstream.close ()
	
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar)#, verbose=True)

	#normalization
	#grammar = getcnf (grammar)
	grammar = get2nf (grammar)

	invUg = odict()
	invUg = getunitrelation(grammar)

	#load source to parse
	
	TokCode = Tokenizer(grammar.tokens)
	TokCode.parse (source)

	#language parser goes here
	langraph = CYKParser (grammar)

	word = TokCode.tokenized
	x = langraph.membership (word, invUg)

	if not x :
		print ('errors n stuff @ ' + str (langraph.err_pos) + 'th token : ' + str(word[langraph.err_pos]))
	else :
		print ('allzgud')
		print (x.unfold())
