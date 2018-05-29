from grammarparser		import *
from graphbuilder		import *
from ChomskyNormalizer 	import *

txtgrammar = """

AXIOM -> S

S -> 
	a.  S  b. |
	''
"""

#integrate "tokens" in grammar definition
#non terminals are tokens pointing on regex
#define language tokens
#terminals' regex
langtokens = [
	('a',		'a'),
	('b',		'b'),
	#('c',		'c'),
	#('d',		'd'),
]

source = """
aaa
bbb
"""

if __name__ == '__main__':
	#parsing
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar)

	print (grammar)
	#dotgraph (grammar, "before_CNF")

	#normalization
	grammar = getnormalform (grammar)

	#print (grammar)
	#dotgraph (grammar, "after_CNF")

	grammar.save ("lang.pkl") #grammar contains everything we want

	#load source to parse
	#print ("source = ", source)
	TokCode = Tokenizer(langtokens)
	TokCode.parse (source)

	#graph generator goes here
	langraph = LanguageGraph (grammar)

	word = TokCode.tokenized

	x = langraph.wordinlanguage (word)
	if not x :
		print ('errors n stuff @ ' + str (langraph.err_pos) + 'th token : ' + str(word[langraph.err_pos]))
	else :
		print ('allzgud')
		print (langraph.path)
