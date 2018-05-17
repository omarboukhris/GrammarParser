from lexlib import Token
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
		production_rules = self.production_rules.copy()
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
		production_rules = self.production_rules.copy()
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
        while self._unit () :
            pass
            
    def _del (self) :
        changed = False
        emptykeys = self._getemptykeys ()
        for remptyk, lemptyk in emptykeys :
            changed = True
            production_rules = self.production_rules.copy()
            out = production_rules.copy()
            for key in production_rules.keys() :

                for rule_index in range(len(production_rules[key])) :

                    #if rule contains runit replace with lunit
                    op_index = self._isoperandinrule (
                        production_rules[key][rule_index], 
                        runitk
                    )
                    
                    if op_index != -1 : #operand is in rule
                        out = self._exploderule (
                            out,
                            key,
                            rule_index,
                            op_index,
                        )
            self.production_rules = out.copy()
        return changed
        

    def _exploderule (self, production_rules, key, rule_index, op_index, lunitk) :

        rule = production_rules[key][rule_index].copy()
        del production_rules[key][rule_index][op_index]
        production_rules[key].append (
            rule
        )
		
        return production_rules
    
    def _isoperandinrule (self, rule, operand) :
        for op_index in range(len(rule)) :
            if rule[op_index].val == operand :
                return op_index
        return -1
    
    def _getemptykeys (self) :
        keys = []
        production_rules = self.production_rules.copy()
        
        for key in production_rules.keys () :
            if key == 'AXIOM' :
                continue
            for r_id in range(len(production_rules[key])) :
                rule = production_rules[key][r_id] 
                if (len(rule) == 1) and (rule[0].type == "EMPTY"):
                    del self.production_rules[key][r_id]
                    if self.production_rules[key] == [] :
                        del self.production_rules[key]
                    keys.append ((key, rule[0].val))
        return keys

class UNIT :
    def __init__ (self, production_rules) :
        self.production_rules = production_rules
    
    def apply (self) :
        while self._unit () :
            pass
            
    def _unit (self) :
        changed = False
        unitkeys = self._getunitkeys ()
        for runitk, lunitk in unitkeys :
            changed = True
            production_rules = self.production_rules
            out = production_rules.copy()
            for key in production_rules.keys() :

                for rule_index in range(len(production_rules[key])) :

                    #if rule contains runit replace with lunit
                    op_index = self._isoperandinrule (
                        production_rules[key][rule_index], 
                        runitk
                    )
                    
                    if op_index != -1 : #operand is in rule
                        out = self._exploderule (
                            out,
                            key,
                            rule_index,
                            op_index,
                            lunitk,
                        )
            self.production_rules = out.copy()
        return changed
        

    def _exploderule (self, production_rules, key, rule_index, op_index, lunitk) :

        rule = production_rules[key][rule_index].copy()
        production_rules[key][rule_index][op_index] = Token("NONTERMINAL", lunitk, '1')
        production_rules[key].append (
            rule
        )
        
        return production_rules
    
    def _isoperandinrule (self, rule, operand) :
        for op_index in range(len(rule)) :
            if rule[op_index].val == operand :
                return op_index
        return -1
    
    def _getunitkeys (self) :
        keys = []
        production_rules = self.production_rules.copy()
        
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






