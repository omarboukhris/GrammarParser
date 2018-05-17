from lexlib import grammarparser as gp, graphbuilder as gb

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
	#TEST_RUN
	grammartokens = [
		('AXIOM',				'AXIOM'),
		('[a-zA-Z_]\w*\.tok',	'TERMINAL'),
		('[a-zA-Z_]\w*',		'NONTERMINAL'),
		('\:=',					'EQUAL'),
		('\+',					'PLUS'),
		('\|',					'OR'),
		('\'\'|\"\"',			'EMPTY'),
	]
	
	AXIOM = r'AXIOM EQUAL NONTERMINAL'
	LSIDE = r'NONTERMINAL EQUAL'
	RSIDE = r'(TERMINAL|NONTERMINAL)+|EMPTY'
	OR, PLUS = r'OR', r'PLUS'
	genericgrammarprodrules = [
		(AXIOM,		'AXIOM'),
		(LSIDE,		'LSIDE'),
		(RSIDE,		'RSIDE'),
		(OR,		'OR'),
		(PLUS,		'PLUS'),
	]

	#lex language => tokenized grammar
	tokenizer = gp.Tokenizer (grammartokens)
	tokenizer.parse (txtgrammar)
	print(tokenizer)

	#lex tokenized grammar => tokenized language
	gram = gp.GenericGrammarParser (genericgrammarprodrules)
	gram.parse (tokenizer)
	print(gram)

	#make production rules
	prodrulesgen = gp.ProductionRulesGenerator ()
	result = prodrulesgen.makeprodrules (
		gram.tokenizedgrammar,
		tokenizer.tokenizedgrammar,
	)

	if (result == (True,[])) :
		prodrulesgen.regularizegrammar()
		print (prodrulesgen)
		prodrulesgen.save("lang.pkl")
	else :
		print (result)

	#graph generator goes here
	"""
	gg = gb.GraphGenerator (prodrulesgen.production_rules)
	axiom = gg.buildgraph()
	#l = axiom.getgraph()
	print (axiom)
	"""
	