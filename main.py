from parselib.grammarparser		import *
from parselib.parsers			import *
from parselib.generaloperators	import *
from parselib.normoperators		import *

import sys

source = """

class my_class2 {
 int f (int blob,) ;
 int c ;
} ;


"""

if __name__ == '__main__':
	
	fstream = open ("expgrammar.grm", "r")
	#fstream = open ("expgrammar.grm", "r")
	txtgrammar = "".join(fstream.readlines())
	fstream.close ()
	
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar) #, verbose=True)

	#normalization
	#grammar = getcnf (grammar)
	grammar = get2nf (grammar)
	print (grammar)
	
	TokCode = Tokenizer(grammar.tokens)
	TokCode.parse (source)

	#language parser goes here
	langraph = CYKParser (grammar, 2)

	word = TokCode.tokenized
	x = langraph.membership (word)

	if not x :
		print ('errors n stuff @ ' + str (langraph.err_pos) + 'th token : ' + str(word[langraph.err_pos]))
	else :
		print ('allzgud')
		print (x[0].unfold())
