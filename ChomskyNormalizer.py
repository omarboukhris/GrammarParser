from lexlib import Token
from collections import OrderedDict as odict
from copy import deepcopy
	
class ChomskyNormalForm :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.normalForm = odict()

	def getnormalform (self) :
		self.normalForm = self.production_rules
		print (self)
		term = TERM (self.production_rules)
		term.apply ()
		#self.normalForm = term.production_rules
		#print (self)
		bins = BIN (term.production_rules)
		bins.apply ()
		#self.normalForm = bins.production_rules
		#print (self)
		dels = DEL (bins.production_rules)
		dels.apply ()
		#self.normalForm = dels.production_rules
		#print ("del" + self.__str__())
		unit = UNIT (dels.production_rules)
		unit.apply ()
		#self.normalForm = unit.production_rules
		#print (self)
		#return  unit.production_rules
		return  unit.production_rules
		
	def __str__ (self) :
		text_rule = ""
		
		for key, rules in self.normalForm.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in self.normalForm[key] :
				rule_in_a_line.append(" + ".join([r.val+"."+r.type+"."+str(r.pos) for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"
		return text_rule


class TERM :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.normalForm = odict()
		
	def apply (self) :
		self._term () 

	def _term (self) :
		normalForm = odict ()
		production_rules = deepcopy(self.production_rules)
		for key, rules in production_rules.items () :
			if not (key in normalForm.keys()) :
				normalForm[key] = []
			for rule in rules :
				normalForm = self.__checkruleforterminals (normalForm, key, rule) 
		self.normalForm = normalForm
		self.production_rules = normalForm

	def __checkruleforterminals (self, normalForm, key, rule) :
		newRule = []
		for i in range (0, len(rule)) :
			operand = rule[i]
			if operand.type == "TERMINAL" :
				newKey = operand.val + "_TOK_NT_"
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
		self._bin ()
		return self.normalForm
	
	def _bin (self) :
		changed = True
		while changed :
			self.normalForm, changed = self._binonce ()

	def _binonce (self) :
		normalForm = odict ()
		production_rules = deepcopy(self.production_rules)
		changed = False
		for key, rules in production_rules.items () :
			if not (key in normalForm.keys ()) :
				normalForm[key] = []
			for rule in rules :
				normalForm = self.__binarizerule (normalForm, key, rule)
				if len(rule) > 2 :
					changed = True
		self.production_rules = normalForm
		return normalForm, changed

	def __binarizerule (self, normalForm, key, rule) :
		if len (rule) <= 2 :
			normalForm[key].append(rule)
		else :
			#newKey = "-".join ([r.val for r in rule[1:]])
			newKey = key + "-".join ([r.val for r in rule[1:]])
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
		while self._del () :
			self.eliminatedoubles ()
			#print (self)
			#pass
			
	def eliminatedoubles (self) :
		production_rules = odict()
		for key in self.production_rules.keys() :
			rules = self.production_rules[key]
			
			uniquerules = []
			banned = []
			for i in range (len (rules)) :
				ruleexists = self.checkunique (uniquerules, rules[i])
				if not ruleexists :
					uniquerules.append (rules [i])

			production_rules[key] = uniquerules
		self.production_rules = production_rules

	def checkunique (self, uniquerules, rule) :
		for r in uniquerules :
			if self.samerule (r, rule) :
				return True
		return False
		
	def samerule (self, rulea, ruleb) :
		if len(rulea) == len(ruleb) :
			for opa, opb in zip (rulea, ruleb) :
				if not (opa.type == opb.type and opa.val == opb.val) : 
					return False
			return True

	def _del (self) :
		
		emptykeys = self._getemptykeys ()
		doubleemptykeys = self._getdoubleemptykeys () 

		#print (emptykeys, doubleemptykeys)
		
		if emptykeys == [] and doubleemptykeys == [] :
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

				exploded, explosion = self._explode1 (rule, emptykeys)
				if exploded :
					for r in explosion :
						node.append (r)

				exploded, explosion = self._explode2 (rule, emptykeys, doubleemptykeys)
				if exploded :
					for r in explosion :
						node.append(r)
				
			if node != [] :
				production_rules[key] = node
		self.production_rules = production_rules
		return True
		
		
	def _explode1 (self, rule, emptykeys) :
		if len(rule) != 1 :
			return False, []

		fixedrules = []
		
		op = rule[0]
		if op.val in emptykeys :
			fixedrules = [[Token("EMPTY", '""', op.pos)]]
		else :
			fixedrules = [rule]
		return True, fixedrules
		
	def _explode2 (self, rule, emptykeys, doubleemptykeys) :
		if len(rule) != 2 :
			return False, []
		
		fixedrules = []
		op1, op2 = rule[0], rule[1]
		
		op1_erasable, op2_erasable = (op1.val in emptykeys), (op2.val in emptykeys)
		op1_nullable, op2_nullable = (op1.val in doubleemptykeys), (op2.val in doubleemptykeys)
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


	
	def _getemptykeys (self) :
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
	
	def _getdoubleemptykeys (self) :
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
	
	def printRule (self, rule) :
		print (" + ".join([r.val+"."+r.type+"."+str(r.pos) for r in rule]))

class UNIT :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
	
	def apply (self) :
		while self._unit () :
			pass
			
	def _unit (self) :
		changed = False
		unitkeys = self._getunitkeys ()

		print (unitkeys)
		#magic happens here

		return changed
	
	def _getunitkeys (self) :
		keys = []
		production_rules = deepcopy(self.production_rules)
		
		for key in production_rules.keys () :
			if key == 'AXIOM' :
				continue
			for r_id in range(len(production_rules[key])) :
				rule = production_rules[key][r_id] 
				if (len(rule) == 1) and (rule[0].type == "NONTERMINAL"):
					del self.production_rules[key][r_id]
					if self.production_rules[key] == [] :
						del self.production_rules[key]
					keys.append ((key, rule[0].val))
		return keys






