from grammarparser		import *
from graphbuilder		import *
from grammaroperations  import *
from ChomskyNormalizer 	import *

txtgrammar = """

;production rules
AXIOM -> S

S ->  
	a. S b. |
;	S b. |
	''

;tokens
;a. -> "a"
;b. -> 'b'

"""

source = "aabb"

langtokens = [
	('a','a'),
	('b','b'),
	#('c', 'c'),
	#('d','d'),
]

if __name__ == '__main__':
	#parsing
	gramparser = GenericGrammarParser ()
	grammar = gramparser.parse (txtgrammar)
	#dotgraph (grammar, "before_CNF")

	#normalization
	print (grammar)
	grammar = getnormalform (grammar)
	print (grammar)
	#dotgraph (grammar, "after_CNF")

	#grammar.save ("lang.pkl") #grammar contains everything we want
	#grammar.load ("lang.pkl")

	#load source to parse
	#print ("source = ", source)
	TokCode = Tokenizer(langtokens)
	TokCode.parse (source)

	#graph generator goes here
	#langraph = LLParser (grammar)
	langraph = CYKParser (grammar)

	word = TokCode.tokenized

	print ()
	for w in word :
		print (w)
	print ()

	x = langraph.wordinlanguage (word, verbose=True)

	if not x :
		print ('errors n stuff @ ' + str (langraph.err_pos) + 'th token : ' + str(word[langraph.err_pos]))
	else :
		print ('allzgud')
		print ("no derivation tree yet")
		#print (langraph.path)
