from collections import OrderedDict as odict

def eliminatedoubles (grammar) :
	production_rules = odict()
	for key in grammar.production_rules.keys() :
		rules = grammar.production_rules[key]
		
		uniquerules = []
		banned = []
		for i in range (len (rules)) :
			ruleexists = checkunique (uniquerules, rules[i])
			if not ruleexists :
				uniquerules.append (rules [i])

		production_rules[key] = uniquerules
	grammar.production_rules = production_rules
	return grammar

def checkunique (uniquerules, rule) :
	for r in uniquerules :
		if samerule (r, rule) :
			return True
	return False
	
def samerule (rulea, ruleb) :
	if len(rulea) == len(ruleb) :
		for opa, opb in zip (rulea, ruleb) :
			if not (opa.type == opb.type and opa.val == opb.val) : 
				return False
		return True
	else :
		return False

def checkproductionrules (production_rules) :
	keys = ["AXIOM"]
	for key, rules in production_rules.items() :
		for rule in rules :
			for operand in rule :
				if (not operand.val in keys) and (operand.type in ["NONTERMINAL", "GENERATOR", "LIST"]) :
					keys.append(operand.val)
	print (production_rules.keys(), "\n",  keys)
	if set(production_rules.keys()) == set(keys) :
		return True, list()
	else :
		return False, list(set(production_rules.keys())-set(keys))

def transformtosource (tokenizedgrammar) :
	source = ""
	for token in tokenizedgrammar :
		source += token.type + " "
	return source


def getnullables (grammar) : #only if binned (less of a headache)
	production_rules = grammar.production_rules
	
	nullables = []
	lenG = 0
	for key, rules in production_rules.items() :
		if rules == [] :
			nullables.append(key)
			continue
		for rule in rules :
			lenG += 1
			
			isruleempty = (len(rule) == 1 and rule[0].type == 'EMPTY')
			if isruleempty :
				nullables.append (key)

	for i in range (lenG) :
		for key, rules in production_rules.items() :

			for rule in rules :
				if len(rule) != 2 :
					continue
				isruleempty = (rule[0].val in nullables and rule[1].val in nullables)
				if isruleempty :
					nullables.append (key)

	return list(set(nullables))

def getinvunitrelation (grammar) :
	nullables = getnullables (grammar)
	
	production_rules = grammar.production_rules
	
	unitrelation = odict()
	
	for key, rules in production_rules.items() :
		for rule in rules :
			isruleunit = (len(rule) == 1 and (not rule[0].type in ['EMPTY', 'TERMINAL']))
			if isruleunit :
				if key in unitrelation.keys() :
					unitrelation[key].append (rule[0].val)
				else :
					unitrelation[key] = [rule[0].val]

	for key, rules in production_rules.items() :
		for rule in rules :
			if len(rule) != 2 :
				continue
			isruleunit = (rule[0].val in nullables)
			if isruleunit :
				if key in unitrelation.keys() :
					unitrelation[key].append (rule[1].val)
				else :
					unitrelation[key] = [rule[1].val]
			
			isruleunit = (rule[1].val in nullables)
			if isruleunit :
				if key in unitrelation.keys() :
					unitrelation[key].append (rule[0].val)
				else :
					unitrelation[key] = [rule[0].val]
	return unitrelation
	




















