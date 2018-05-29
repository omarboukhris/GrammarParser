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
		x = self.checkNode (word, 'AXIOM') 
		return x and self.cursor == len(word)

	def checkNode (self, word, rulename) :
		for rule in self.production_rules[rulename] :
			if self.dorule (word, rule) :
				return True
		return False

	def checkToken (self, word, tokentype) :
		if self.cursor >= len(word) :
			return False
		if word[self.cursor].type == tokentype :
			self.cursor += 1
			return True
		return False

	def dorule (self, word, rule) :
		for operand in rule :
			success = self.dooperand  (word, operand)
			if not success :
				return False 
		return True

	def dooperand (self, word, operand) :
		curs = int(self.cursor)
		if operand.type == "NONTERMINAL" :
			if not self.checkNode (word, operand.val) :
				self.cursor = int(curs)
				return False
			else :
				return True
		else :
			return self.checkToken(word, operand.val) 
