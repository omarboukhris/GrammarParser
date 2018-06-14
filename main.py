from grammarparser		import *
from graphbuilder		import *
from grammaroperations  import *
from ChomskyNormalizer 	import *

import sys

source = """
class myclass {
	public int c ;
} ;
"""

if __name__ == '__main__':
	
	fstream = open ("grammar.grm", "r")
	txtgrammar = "".join(fstream.readlines())
	fstream.close ()
	
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar)#, verbose=True)
	#dotgraph (grammar, "before_CNF")

	#normalization
	print (grammar)
	grammar = getnormalform (grammar)
	##dotgraph (grammar, "after_CNF")
	grammar.save ("lang.pkl") #grammar contains everything we want
	grammar.load ("lang.pkl")
	print (grammar)
	
	#load source to parse
	TokCode = Tokenizer(grammar.langtokens)
	TokCode.parse (source)

	#graph generator goes here
	#langraph = LLParser (grammar)
	langraph = CYKParser (grammar)

	word = TokCode.tokenized

	#print ()
	#for w in word :
		#print (w)
	#print ()

	x = langraph.wordinlanguage (word, verbose=True)

	if not x :
		print ('errors n stuff @ ' + str (langraph.err_pos) + 'th token : ' + str(word[langraph.err_pos]))
	else :
		print ('allzgud')
		print ("no derivation tree yet")
		#print (langraph.path)
