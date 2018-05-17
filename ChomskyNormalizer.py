from lexlib.lexlib import Token
from collections import OrderedDict as odict

	
class ChomskyNormalForm :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.normalForm = odict()

	def getnormalform (self) :
		term = TERM (self.production_rules)
		term.apply ()
		bins = BIN (term.production_rules)
		bins.apply ()
		dels = DEL (bins.production_rules)
		dels.apply ()
		self.normalForm = dels.production_rules
		print (self)
		unit = UNIT (dels.production_rules)
		unit.apply ()
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
		production_rules = self.production_rules
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
		production_rules = self.production_rules
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
		self.normalForm = production_rules #odict
	
	def apply (self) :
		self._del ()
		self.production_rules = self.normalForm

	def _del (self) :
		emptykeys = self._getemptykeys()
		while emptykeys != [] :
			emptykeys = self._getemptykeys()
			for key in emptykeys :
				self._delEmpty (key)

			for key in emptykeys :
				#for each rule using an empty non terminal, delete the void (empty) element
				self.cleanup()
				self._scrapempty (key)

	def cleanup (self) :
		for key, rules in self.normalForm.items() :
			if rules == [] :
				del self.normalForm[key]

	def _scrapempty (self, key) :
		normalForm = odict()
		production_rules = self.normalForm
		for label, rules in production_rules.items () :
			normalForm[label] = []
			for rule in rules :
				if rule == [] :
					continue
				if key in [op.val for op in rule] :
					if len (rule) == 1 :
						continue
					newRules = [rule]
					newRules.append([op for op in rule if op.val != key])
					normalForm[label] += newRules
				else :
					normalForm[label].append(rule)
		self.normalForm = normalForm


	def _delEmpty (self, key) :
		copyNonTerminal = []
		production_rules = self.normalForm
		for rule in production_rules[key] :
			newrule = []
			for operand in rule :
				if operand.type != "EMPTY" :
					newrule.append (operand)
			if newrule != [] :
				copyNonTerminal.append (newrule)
		self.normalForm[key] = copyNonTerminal
		if self.normalForm[key] == [] :
			del self.normalForm[key]

	def _getemptykeys (self) :
		keys = []
		for key, rules in self.normalForm.items() :
			if key == "AXIOM" : 
				continue
			for rule in rules :
				if rule[0].type == "EMPTY" or (rule[0].val == key and len(rule) == 1) :
					keys.append(key)
		return list(set(keys))

	
	def __str__ (self) :
		text_rule = ""
		
		for key, rules in self.normalForm.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in rules :
				rule_in_a_line.append(" + ".join([r.val+"."+r.type+"."+str(r.pos) for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"
		return text_rule

class UNIT :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.normalForm = production_rules #odict
	
	def apply (self) :
		self._unit ()
		self.production_rules = self.normalForm

	def _unit (self) :
		unitkeys = self._getunitkeys()
		while unitkeys != [] :
			for key in unitkeys :
				self._delunit (key)

			for key in unitkeys :
				#for each rule using an empty non terminal, delete the void (empty) element
				self.cleanup()
				self._scrapunit (key)

	def cleanup (self) :
		for key, rules in self.normalForm.items() :
			if rules == [] :
				del self.normalForm[key]

	def _scrapunit (self, key) :
		normalForm = odict()
		production_rules = self.normalForm
		for label, rules in production_rules.items () :
			normalForm[label] = []
			for rule in rules :
				if rule == [] :
					continue
				if key[0] in [op.val for op in rule] :
					newRules = [rule]
					arule = []
					for operand in rule :
						arule.append(operand if operand.val != key[0] else key[1])
					newRules.append(arule)
					normalForm[label] += newRules
				else :
					normalForm[label].append(rule)
		self.normalForm = normalForm

	def _delunit (self, _key) : 
		key = _key[0]
		copyNonTerminal = []
		production_rules = self.normalForm
		for rule in production_rules[key] :
			newrule = []
			for operand in rule :
				if rule[0].type != "NONTERMINAL" or len(rule) != 1 :
					newrule.append (operand)
			if newrule != [] :
				copyNonTerminal.append (newrule)
		self.normalForm[key] = copyNonTerminal
		if self.normalForm[key] == [] :
			del self.normalForm[key]

	def _getunitkeys (self) :
		keys = []
		for key, rules in self.normalForm.items() :
			if key == "AXIOM" :
				continue
			for rule in rules :
				if rule[0].type == "NONTERMINAL" and len(rule) == 1 :
					keys.append((key, rule[0]))
		return list(set(keys))







