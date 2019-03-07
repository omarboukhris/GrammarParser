from parselib.grammarparser		import *
from parselib.parsers			import *
from parselib.generaloperators	import *
from parselib.normoperators		import *

import sys

source = """
class myclass {
 public int c ;
 public int c () {} ;
} ;
class myclass {
 public int c ;
 public int c () {} ;
 public int c () {} ;
} ;"""

if __name__ == '__main__':
	
	fstream = open ("grammar.grm", "r")
	txtgrammar = "".join(fstream.readlines())
	fstream.close ()
	
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar, verbose=True)

	#normalization
	#grammar = getcnf (grammar)
	grammar = get2nf (grammar)

	#get tokens from source code
	TokCode = Tokenizer(grammar.tokens)
	TokCode.parse (source)

	#language parser instanciated here
	langraph = CYKParser (grammar)

	word = TokCode.tokenized
	x = langraph.membership (word)

	if not x :
		print (x) # x should point errors out if parsing failed
	else :
		print (len(x)) #possible parse trees
		print (x[0]) #x[0] most pertinent solution
