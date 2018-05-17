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
	gram = gp.GenericGrammarParser (genericgrammarprodrules)
	gram.parse (txtgrammar)
	print(gram)

	#graph generator goes here
	"""
	gg = gb.GraphGenerator (prodrulesgen.production_rules)
	axiom = gg.buildgraph()
	#l = axiom.getgraph()
	print (axiom)
	"""
	