from grammarparser		import *
from graphbuilder		import *
from ChomskyNormalizer 	import *

txtgrammar = """

AXIOM := S

S := 
	a. + S + d. | 
	''

"""

#integrate "tokens" in grammar definition
#non terminals are tokens pointing on regex
#define language tokens
#terminals' regex
langtokens = [
	('a',		'a'),
	('d',		'd'),
	#('class',	'CLASS_DECL'),
]

source = "aaaddd"

if __name__ == '__main__':
	#parsing
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar)
	
	#print (grammar)
	#dotgraph (grammar, "before_CNF")

	#normalization
	grammar = getnormalform (grammar)

	print (grammar)
	#dotgraph (grammar, "after_CNF")

	grammar.save ("lang.pkl") #grammar contains everything we want

	#load source to parse
	TokCode = Tokenizer(langtokens)
	TokCode.parse (source)

	#graph generator goes here
	langraph = LanguageGraph (grammar)

	for letter in TokCode.tokenized :
		print (letter)

	x = langraph.wordinlanguage (TokCode.tokenized)
	if not x :
		#for letter in w :
			#print (letter)
		print ('errors n stuff')
	else :
		print (x)
		print ('allzgoud')
	
