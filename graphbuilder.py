from collections import OrderedDict as odict
import os

def dotgraph (gram, filename) :
	ss = "graph {\n"
	for key, rules in gram.production_rules.items() :
		for rule in rules :
			r = [op.val for op in rule]
			r = [i.replace ("-", "") for i in r]
			r = [i.replace ("\'\'", "eps") for i in r]
			r = [i.replace ("\"\"", "eps") for i in r]
			k = key.replace ("-", "")
			ss += "\t" + k + " -- " 
			ss += " -- ".join (r)
			ss += " ;\n"
	ss += "}"
	filestream = open (filename + '.dot', 'w') 
	filestream.write(ss)
	filestream.close ()
	cmd = 'dot -Tpng -o ' + filename + '.png ' + filename + '.dot'
	os.system (cmd)
	cmd = 'rm ' + filename + '.dot'
	os.system (cmd)

class LanguageGraph :
	def __init__ (self, grammar) :
		self.production_rules = grammar.production_rules

	def wordinlanguage (self, word, rulename="AXIOM") :
		print ("rulename : " + rulename + " : " + " ".join ([
			w.val for w in word
		]))
		if len(word) == 0 :
			return True, []
		for transition in self.production_rules[rulename] :
			if self.dotransition (word, transion) :
				return True, []
		return False, word


			x = False
			ex_word = word.copy()
			if len(transition) == 1 :
				x, word = self._transit_1 (word, transition[0])
			else : #len == 2
				x, word = self._transit_1 (word, transition[0])
				if x and len(word) != 0 : 
					x, word = self._transit_1 (word, transition[1])
				else :
					x = False
			if x and len(word) == 0 :
				return True, []
			else :
				word = ex_word.copy()
			
		return False, word

			#if transition[0].type == "TERMINAL" : #left terminal
				#print ('terminal ' + transition[0].val)
				##(x, word) = self.checkToken (word, transition[0].val)
				#return self.checkToken (word, transition[0].val)
			
			#elif (transition[0].type == "NONTERMINAL") : #left nonterminal
				#print ('nonterminal ' + transition[0].val )
				#(x, word) = self.wordinlanguage (word, transition[0].val)

			#if (x and len(transition) > 1 and word != []) : #right operand if any
				#print ('len sup 2 ' + transition[1].val )
				#(x, word) = self.wordinlanguage (word, transition[1].val)

			#if x and word == [] :
				#return True, []

		#return False, word
		
	def _transit_1 (self, word, transition) :
		if transition.type == "TERMINAL" :
			if transition.val == word[0].val :
				return True, word[1:]
			else :
				return False, word
		else :
			return self.wordinlanguage(word, transition.val)
		
		
 
	def checkToken (self, symb, tokentype) :
		cond = symb[0].val == tokentype
		symb = symb[1:] if cond else symb
		return cond, symb
