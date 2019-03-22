from parselib.grammarparser		import *
from parselib.parsers			import *
from parselib.generaloperators	import *
from parselib.normoperators		import *
from parselib.intermediateparser	import *

import sys, json


def processResults (x, verbose=True) :
	""" Unfolds the parse tree and optionnaly prints it
	
        Parameters
        ----------
        x : UnitNode, TokenNode, BinNode from parselib.parsetree
			a list of the folded possible parse trees
		verbose : bool
			True (by default) to print results, otherwise False
	"""
	if not x :
		if verbose : print (x) # x should point errors out if parsing failed
		return None
	else :
		if verbose : print ('number of possible parse trees : ', len(x))
		parsedrawdict = x[0].unfold() #all parse tree unfold the same
		if verbose : print (parsedrawdict)
		return parsedrawdict 
	
def loadAsText (filename) :
	"""returns raw text read from file
	
	Parameters
	----------
	filename : str
		string path to file containing text to load
	"""
	fs = open(filename, "r")
	source = "".join(fs.readlines())
	fs.close()
	return source

if __name__ == '__main__':
	
	#================ BEGIN : Grammar parsing
	
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (
		loadAsText("data/grammar.grm"),
		#loadAsText("data/grammarvo2.grm"),
		verbose=True
	)

	#normalization
	#grammar = getcnf (grammar)
	grammar = get2nf (grammar)
	print (grammar)
	
	grammar.save("data/somewhere.pkl")
	#================ END : Grammar parsing

	#================ BEGIN : membership test
	grammar.load("data/somewhere.pkl")
	
	#get tokens from source code
	TokCode = Tokenizer(grammar.tokens)
	TokCode.parse (
		loadAsText ("data/test.java")
	)

	#language parser instanciated here
	langraph = CYKParser (grammar)

	word = TokCode.tokenized
	x = langraph.membership (word)
	sourced = processResults (x)
	#================ END : membership test

	#================ BEGIN : source code retokenizing
	interm = IntermediateParser()
	interm.parse (
		sourced, 
		verbose=True
	)
	#================ END : source code retokenizing

















