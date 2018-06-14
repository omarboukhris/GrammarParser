from grammarparser		import *
from graphbuilder		import *
from grammaroperations  import *
from ChomskyNormalizer 	import *

import sys

txtgrammar = """
AXIOM -> class

class ->  
	classdec. identifier. lcrch. classbody rcrch. semic. class |
;	''
	''
;;

classbody -> 
	visibility. identifier. identifier. lpar. listparam rpar. semic. classbody |
	visibility. identifier. identifier. semic. classbody |
	''

listparam -> 
	identifier. identifier. |
	identifier. identifier. comma. listparam |
	''
"""

identifier = r"[a-zA-Z_]\w*"

langtokens = [
	("class"						, "classdec"),
	("(public|private|protected)"	, "visibility"),
	("\{"							, "lcrch"),
	("\}"							, "rcrch"),
	("\("							, "lpar"),
	('\)'							, "rpar"),
	("\;"							, "semic"),
	(identifier						, "identifier"),
]
	
source = """
class myclass {
	public int c ;
} ;
"""

if __name__ == '__main__':
	#parsing
	if len(sys.argv) == 2 :
		source = sys.argv[1]
	
	print (source)
	
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
