from collections import OrderedDict as odict

class LanguageGraph :
	def __init__ (self, production_rules=odict) :
		self.production_rules = production_rules

	def wordinlanguage (self, word, rulename="AXIOM") :
		if word == [] :
			return True, []
		for transition in self.production_rules[rulename] :
			x = False
			if transition[0].type == "TERMINAL" : #left terminal
				(x, word) = self.checkToken (word, transition[0].val)
			
			elif (transition[0].type == "NONTERMINAL") : #left nonterminal
				(x, word) = self.wordinlanguage (word, transition[0].val)

			if (x and len(transition) > 1 and word != []) : #right operand if any
				x = self.wordinlanguage (word, transition[1].val)

			if x and word == [] :
				return True, []

		return x, word
 
	def checkToken (self, symb, tokentype) :
		cond = symb[0].val == tokentype
		symb = symb[1:] if cond else symb
		return cond, symb
