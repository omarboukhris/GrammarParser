from lexlib import grammarparser as gp

txtgrammar = """
AXIOM := S
S     	 := 
	'A' B C |
	A 'B'
A := 
	'B' C
B :=
	'B' C |
	'B'
C := 
	'C' |
	' '
"""

if __name__ == '__main__':
	#TEST_RUN
	grammartokens = [
		('AXIOM',			'AXIOM'),
		('[a-zA-Z_]\w*',	'NONTERMINAL'),
		('\'.*\'',			'TERMINAL'),
		('\:=',				'EQUAL'),
		('\|',				'OR'),
	]
	
	AXIOM = r'AXIOM EQUAL NONTERMINAL'
	LSIDE = r'NONTERMINAL EQUAL' 
	RSIDE = r'(TERMINAL|NONTERMINAL)+ '
	OR = r'OR'
	genericgrammarprodrules = [
		(AXIOM, 'AXIOM'),
		(LSIDE, 'LSIDE'),
		(RSIDE, 'RSIDE'),
		(OR,	'OR'),
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
	prodrulesgen.makeprodrules (
		gram.tokenizedgrammar,
		tokenizer.tokenizedgrammar,
	)
	print (prodrulesgen)
	prodrulesgen.save("blob.pkl")
	
	#graph generator goes here



	