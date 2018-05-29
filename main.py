from grammarparser		import *
from graphbuilder		import *
from ChomskyNormalizer 	import *

txtgrammar = """

AXIOM -> S

S -> 
	a.  S  b. |
	''

a. -> "a"
b. -> 'b'
"""

source = """
aaa
bbb
"""

if __name__ == '__main__':
	#parsing
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar)
	#dotgraph (grammar, "before_CNF")

	#normalization
	grammar = getnormalform (grammar)
	print (grammar)
	#dotgraph (grammar, "after_CNF")

	#grammar.save ("lang.pkl") #grammar contains everything we want
	#grammar.load ("lang.pkl")

	#load source to parse
	#print ("source = ", source)
	TokCode = Tokenizer(grammar.langtokens)
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
