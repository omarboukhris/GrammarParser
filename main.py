from grammarparser		import *
from graphbuilder		import *
from ChomskyNormalizer 	import *

txtgrammar = """
AXIOM := CLASS
CLASS := 
		CL.tok + A |
		FK + B + VF.tok + DC.tok

FK := 
	FL.tok 

A := 
	LC.tok + B + RC.tok |
	B

B :=
	B |
	C

C := 
	''
"""

txtgrammar = """

AXIOM := S

S := 
	a.tok + S + d.tok | 
	''

"""
#A := a.tok + A + S |
	#B A |
	#B | 
	#C
	
#B := '' |
	#C |
	#C d.tok |
	#d.tok
#C := ''
#"""

#DC := NOK.tok
#integrate "tokens" in grammar definition
#non terminals are tokens pointing on regex
#define language tokens
#terminals' regex
langtokens = [
	('a',		'a'),
	('d',		'd'),
	#('class',	'CLASS_DECL'),
]

source = "aadd"

if __name__ == '__main__':
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar, verbose=True)
	
	dotgraph (grammar, "before_CNF")
	grammar = getnormalform (grammar)
	print (grammar)
	dotgraph (grammar, "after_CNF")

	grammar.save ("lang.pkl") #grammar contains everything we want

	#load source to parse
	TokCode = Tokenizer(langtokens)
	TokCode.parse (source)
	

	#graph generator goes here
	langraph = LanguageGraph (grammar)

	x, w = langraph.wordinlanguage (TokCode.tokenized)
	if not x :
		for letter in w :
			print (letter)
	else :
		print (w, x)
		print ('allzgoud')
	
