from parselib.grammarparser		import *
from parselib.parsers			import *
from parselib.generaloperators	import *
from parselib.normoperators		import *

import sys, json

source = """
class myclass {
 class tmp { } ;
 public int a ;
 public int b () {} ;
 public int b2 () {} ;
 public int b3 () {} ;
} ;
class myclass2 {
 public int c ;
 public int d () {} ;
 public int e () {} ;
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
	print (grammar)
	
	grammar.save("somewhere.pkl")
	grammar.load("somewhere.pkl")
	
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
		print ('number of possible parse trees : ', len(x)) #possible parse trees
		#x[0].setuplabels(grammar.labels)
		parsedrawdict = x[0].unfold()
		print (json.dumps(parsedrawdict, indent=3)) #x[0] most pertinent solution
		#print (cleanparsed(grammar, parsedrawdict))

