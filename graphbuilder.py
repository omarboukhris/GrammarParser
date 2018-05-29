from collections import OrderedDict as odict
import os

def dotgraph (gram, filename) :
	ss = "graph {\n"
	for key, rules in gram.production_rules.items() :
		for rule in rules :
			r = [op.val for op in rule]
			r = [i.replace ("-", "") for i in r]
			r = [i.replace (".", "_tok") for i in r]
			r = [i.replace ("\'\'", "eps") for i in r]
			r = [i.replace ("\"\"", "eps") for i in r]
			k = key.replace ("-", "")
			k = k.replace (".", "_tok")
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
		self.cursor = None

	def wordinlanguage (self, word) :
		if len(word) == 0 :
			return True
		self.cursor = 0
		x = self.doproductionrule (word, 'AXIOM') 
		return x and self.cursor == len(word)

	def doproductionrule (self, word, rulename) :

		for transition in self.production_rules[rulename] :
			#print (
				#str(self.cursor) + ' ' + rulename + ':' + 
				#' '.join([tr.val for tr in transition]) + '|' + 
				#' '.join ([w.val for w in word])
			#)

			x = self.dotransition (word, transition)

			if x :
				return True

		return False
		
	def dotransition (self, word, transition) :
		for operand in transition :
			#success = self.dooperand (word, operand)
			success = self.dooperand_debug (word, operand)
			if not success :
				return False 
		return True

	def dooperand_debug (self, word, operand) :
		return self.doproductionrule (word, operand.val) if operand.type == "NONTERMINAL" else self.checkToken(word, operand.val) 

	def dooperand (self, word, operand) :
		curs = int(self.cursor)

		if operand.type == "TERMINAL" :
			return self.checkToken(word, operand.val) 
		
		if operand.type == "NONTERMINAL" :
			success = self.doproductionrule (word, operand.val)
			if not success :
				self.cursor = int(curs)
				return False
			else :
				return True

	def checkToken (self, word, tokentype) :
		if self.cursor >= len(word) :
			return False
		if word[self.cursor].type == tokentype :
			self.cursor += 1
			return True
		return False
