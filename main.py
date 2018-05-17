import grammarparser as gp
import graphbuilder as gb

txtgrammar = """
AXIOM := CLASS
CLASS := 
		CLASS_DECL.tok + A |
		FUNK + B + VF.tok + DC.tok

FUNK := 
	FDECL.tok |
	""

A := 
	LCROCH.tok + B + RCROCH.tok |
	''

B :=
	B |
	C

C := 
	''
"""

txtgrammar = """

AXIOM := S

S := a.tok + A |
''

A := a.tok + A + S |
	A B |
	A
	
B := ''

"""


#DC := NOK.tok
#integrate "tokens" in grammar definition
#non terminals are tokens pointing on regex
#define language tokens
#terminals' regex
langtokens = [
	('{{',		'LCROCH'),
	('}}',		'RCROCH'),
	('class',	'CLASS_DECL'),
]

if __name__ == '__main__':
	gram = gp.GenericGrammarParser (txtgrammar)
	gram.parse (verbose=True)

	#graph generator goes here
	"""
	gg = gb.GraphGenerator (prodrulesgen.production_rules)
	axiom = gg.buildgraph()
	#l = axiom.getgraph()
	print (axiom)
	"""
	