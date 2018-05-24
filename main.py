import grammarparser as gp
import graphbuilder as gb

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

#txtgrammar = """

#AXIOM := S

#S := a.tok + A 

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
	('{{',		'LCROCH'),
	('}}',		'RCROCH'),
	('class',	'CLASS_DECL'),
]

if __name__ == '__main__':
	gramparser = gp.GenericGrammarParser (txtgrammar)
	grammar = gramparser.parse (verbose=True)

	grammar.save ("lang.pkl")

	#graph generator goes here

	"""
	gg = gb.GraphGenerator (prodrulesgen.production_rules)
	axiom = gg.buildgraph()
	#l = axiom.getgraph()
	print (axiom)
	"""

