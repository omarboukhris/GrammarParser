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
				if (not operand.val in keys) and (operand.type == "NONTERMINAL") :
					keys.append(operand.val)
	if set(production_rules.keys()) == set(keys) :
		return True, list()
	else :
		return False, list(set(production_rules.keys())-set(keys))

def transformtosource (tokenizedgrammar) :
	source = ""
	for token in tokenizedgrammar :
		source += token.type + " "
	return source


