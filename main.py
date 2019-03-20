from parselib.grammarparser		import *
from parselib.parsers			import *
from parselib.generaloperators	import *
from parselib.normoperators		import *

import sys, json

def streamResults (x) :
	if not x :
		print (x) # x should point errors out if parsing failed
	else :
		print ('number of possible parse trees : ', len(x))
		parsedrawdict = x[0].unfold()
		print (parsedrawdict)
		#print (json.dumps(parsedrawdict, indent=3)) #x[0] most pertinent solution

def loadAsText (filename) :
	fs = open(filename, "r")
	source = "".join(fs.readlines())
	fs.close()
	return source

if __name__ == '__main__':
	
	#================ BEGIN : Grammar parsing
	
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (
		loadAsText("grammar.grm"),
		verbose=True
	)

	#normalization
	#grammar = getcnf (grammar)
	grammar = get2nf (grammar)
	print (grammar)
	
	grammar.save("somewhere.pkl")
	#================ END : Grammar parsing

	#================ BEGIN : membership test
	grammar.load("somewhere.pkl")
	
	#get tokens from source code
	TokCode = Tokenizer(grammar.tokens)
	TokCode.parse (
		loadAsText ("test.java")
	)

	#language parser instanciated here
	langraph = CYKParser (grammar)

	word = TokCode.tokenized
	x = langraph.membership (word)
	streamResults (x)
	#================ END : membership test

