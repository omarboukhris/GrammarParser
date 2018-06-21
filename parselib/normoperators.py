from parselib.lexlib import Token
from parselib.generaloperators import eliminatedoubles
from collections import OrderedDict as odict
from copy import deepcopy

def getcnf (grammar) :
	production_rules = grammar.production_rules
	term = TERM (production_rules)
	term.apply ()
	bins = BIN (term.production_rules)
	bins.apply ()
	dels = DEL (bins.production_rules)
	dels.apply ()
	unit = UNIT (dels.production_rules)
	unit.apply ()
	grammar.production_rules = unit.production_rules
	return grammar

def get2nf (grammar) :
	production_rules = grammar.production_rules
	term = TERM (production_rules)
	term.apply ()
	bins = BIN (term.production_rules)
	bins.apply ()
	grammar.production_rules = bins.production_rules
	
	return eliminatedoubles(grammar)

class TERM :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.normalForm = odict()
		
	def apply (self) :
		self.term () 

	def term (self) :
		normalForm = odict ()
		production_rules = deepcopy(self.production_rules)
		for key, rules in production_rules.items () :
			if not (key in normalForm.keys()) :
				normalForm[key] = []
			for rule in rules :
				normalForm = self.checkruleforterminals (normalForm, key, rule) 
		self.normalForm = normalForm
		self.production_rules = normalForm

	def checkruleforterminals (self, normalForm, key, rule) :
		newRule = []
		for i in range (0, len(rule)) :
			operand = rule[i]
			if operand.type == "TERMINAL" :
				newKey = operand.val + "."
				if not (newKey in self.normalForm.keys()) :
					normalForm[newKey] = []
				normalForm[newKey].append([operand])
				newRule.append(Token ("NONTERMINAL", newKey, operand.pos))
			else :
				newRule.append(operand)
		normalForm[key].append(newRule)
		return normalForm

class BIN :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.normalForm = odict()

	def apply (self) :
		self.binarize ()
		return self.normalForm
	
	def binarize (self) :
		changed = True
		while changed :
			self.normalForm, changed = self.binonce ()

	def binonce (self) :
		normalForm = odict ()
		production_rules = deepcopy(self.production_rules)
		changed = False
		for key, rules in production_rules.items () :
			if not (key in normalForm.keys ()) :
				normalForm[key] = []
			for rule in rules :
				normalForm = self.binarizerule (normalForm, key, rule)
				if len(rule) > 2 :
					changed = True
		self.production_rules = normalForm
		return normalForm, changed

	def binarizerule (self, normalForm, key, rule) :
		if len (rule) <= 2 :
			normalForm[key].append(rule)
		else :
			newKey = "/".join ([r.val.strip('.') for r in rule[1:]])
			#newKey = key + "-".join ([r.val for r in rule[1:]])
			if not (newKey in normalForm.keys()) :
				normalForm[newKey] = []
			newProdRule = rule[1:]
			normalForm[key].append([rule[0], Token ("NONTERMINAL", newKey, rule[1].pos)])
			normalForm[newKey].append(newProdRule)
		return normalForm

#grammar must be binned
class DEL :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
	
	def apply (self) :
		#print (self)
		while self.appdel () :
			self = eliminatedoubles (self)

	def appdel (self) :
		
		emptykeys = self.getemptykeys ()
		superemptykeys = self.getsuperemptykeys () 

		#print (emptykeys, doubleemptykeys)
		
		if emptykeys == [] and superemptykeys == [] :
			return False
		
		
		production_rules = odict ()
		for key in self.production_rules.keys () :
			if key == "AXIOM" :
				production_rules[key] = self.production_rules[key]
				continue
			production_rules[key] = []
			node = []

			rules = self.production_rules[key]

			for rule in rules :

				exploded, explosion = self.explode_unit_rules (rule, emptykeys)
				if exploded :
					for r in explosion :
						node.append (r)

				exploded, explosion = self.explode_bin_rules (rule, emptykeys, superemptykeys)
				if exploded :
					for r in explosion :
						node.append(r)
				
			if node != [] :
				production_rules[key] = node
		self.production_rules = production_rules
		return True
		
		
	def explode_unit_rules (self, rule, emptykeys) :
		if len(rule) != 1 :
			return False, []

		fixedrules = []
		
		op = rule[0]
		if op.val in emptykeys :
			fixedrules = [[Token("EMPTY", '""', op.pos)]]
		else :
			fixedrules = [rule]
		return True, fixedrules
		
	def explode_bin_rules (self, rule, emptykeys, superemptykeys) :
		if len(rule) != 2 :
			return False, []
		
		fixedrules = []
		op1, op2 = rule[0], rule[1]
		
		op1_erasable, op2_erasable = (op1.val in emptykeys), (op2.val in emptykeys)
		op1_nullable, op2_nullable = (op1.val in superemptykeys), (op2.val in superemptykeys)
		op1_allcool, op2_allcool = (not op1_erasable and not op1_nullable), (not op2_erasable and not op2_nullable)
		
		if op1_erasable and op2_erasable :
			fixedrules.append (
				[Token("EMPTY", '""', op1.pos)]
			)
		elif op1_erasable and op2_nullable :
			fixedrules.append (
				[Token("EMPTY", '""', op1.pos)]
			)
			fixedrules.append (
				[op2]
			)
		elif op1_erasable and op2_allcool :
			fixedrules.append (
				[op2]
			)
		elif op1_nullable and op2_erasable :
			fixedrules.append (
				[Token("EMPTY", '""', op1.pos)]
			)
			fixedrules.append (
				[op1]
			)
		elif op1_nullable and op2_nullable :
			fixedrules.append (
				[Token("EMPTY", '""', op1.pos)]
			)
			fixedrules.append (
				[op1]
			)
			fixedrules.append (
				[op2]
			)
			fixedrules.append (
				[op1, op2]
			)
		elif op1_nullable and op2_allcool :
			fixedrules.append (
				[op2]
			)
			fixedrules.append (
				[op1, op2]
			)
		elif op1_allcool and op2_erasable :
			fixedrules.append (
				[op1]
			)
		elif op1_allcool and op2_nullable :
			fixedrules.append (
				[op1, op2]
			)
			fixedrules.append (
				[op1]
			)
		elif op1_allcool and op2_allcool :
			fixedrules.append (
				[op1, op2]
			)
		return True, fixedrules


	
	def getemptykeys (self) :
		production_rules = odict ()
		keys = []
		for key, rules in self.production_rules.items() :
			if rules == [] :
				keys.append(key)
				continue
			production_rules[key] = []
			for rule in rules :
				
				isruleempty = (len(rules) == 1 and len(rule) == 1 and rule[0].type == 'EMPTY')
				isruleonself = (len(rules) == 1 and len(rule) == 1 and rule[0].val == key)
				
				if isruleempty or isruleonself :
					keys.append (key)
				else :
					production_rules[key].append(rule)
		self.production_rules = production_rules
		return list(set(keys))

	def getsuperemptykeys (self) :
		production_rules = odict ()
		keys = []
		for key, rules in self.production_rules.items() :
			if rules == [] :
				continue
			production_rules[key] = []
			for rule in rules :
				if len(rules) > 1 and len(rule) == 1 and rule[0].type == 'EMPTY' :
					keys.append (key)
				else :
					production_rules[key].append(rule)
		self.production_rules = production_rules
		return list(set(keys))
		
	def __str__ (self) :
		text_rule = ""
		self.normalForm = self.production_rules
		for key, rules in self.normalForm.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in self.normalForm[key] :
				rule_in_a_line.append(" + ".join([r.val+"."+r.type+"."+str(r.pos) for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"
		return text_rule

class UNIT :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
	
	def apply (self) :
		while self.unit () :
			self = eliminatedoubles (self)
	
	def unit (self) :
		unitkeys, superunitkeys = self.getunitkeys ()

		
		if unitkeys == {} and superunitkeys == {} :
			return False
		
		production_rules = odict()

		for key, rules in self.production_rules.items() :
			production_rules[key] = rules
			if key in superunitkeys.keys () :
				for repl in superunitkeys[key] :
					if repl in superunitkeys.keys() or repl in unitkeys.keys() :
						continue
					production_rules[key] += self.production_rules[repl]

		self.production_rules = production_rules
		return True

	def getunitkeys (self) :
		production_rules = odict()
		unitkeys, superunitkeys = {}, {}
		for key, rules in self.production_rules.items () :
			if key == 'AXIOM' :
				production_rules["AXIOM"] = self.production_rules["AXIOM"]
				continue
			node = []
			rules = self.production_rules[key]
			if len(rules) == 1 :
				rule = rules[0]
				if len(rule) == 1 and rule[0].type == "NONTERMINAL" :#and (rule[0].val[-8:] != '_TOK_NT_' or rule[0].val[-1:] != '.') :
					unitkeys[key] = rule[0].val
				else :
					node = rules
			else :
				keyslist = []
				for rule in rules :
					if len(rule) == 1 and rule[0].type == "NONTERMINAL" :# and (rule[0].val[-8:] != '_TOK_NT_' or rule[0].val[-1:] != '.') :
						if rule[0].val != key :
							keyslist.append(rule[0].val)
					else :
						node.append(rule)
				if keyslist != [] : 
					superunitkeys[key] = keyslist
			if node != [] :
				production_rules[key] = node
		self.production_rules = production_rules
		return unitkeys, superunitkeys
