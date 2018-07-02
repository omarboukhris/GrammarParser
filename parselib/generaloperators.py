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

#check if semi-proper grammar (if all non terminals used got defined)
def checkproductionrules (production_rules) :
	keys = ["AXIOM"]
	for key, rules in production_rules.items() :
		for rule in rules :
			for operand in rule :
				if (not operand.val in keys) and (not operand.type in ["TERMINAL", "LABEL", "LABELATOR", "EMPTY"]) :
					keys.append(operand.val)
	if set(production_rules.keys())-set(keys) == set() :
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

def removenullables (grammar) :
	production_rules = odict()
	for key, rules in grammar.production_rules.items() :
		production_rules[key] = []
		for rule in rules :
			if len(rule) == 1 and rule[0].type == "EMPTY" :
				continue
			production_rules[key].append(rule)
	grammar.production_rules = production_rules
	return grammar

def getunitrelation (grammar) :
	nullables = getnullables (grammar)
	
	production_rules = grammar.production_rules
	
	unitrelation = odict()
	
	for key, rules in production_rules.items() :
		#if key == "AXIOM" :
			#continue
		for rule in rules :
			isruleunit = (len(rule) == 1 and (not rule[0].type in ['EMPTY', 'TERMINAL']))
			if isruleunit :
				if key in unitrelation.keys() :
					unitrelation[key].append (rule[0].val)
				else :
					unitrelation[key] = [rule[0].val]

	for key, rules in production_rules.items() :
		#if key == "AXIOM" :
			#continue
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

	### propagates unit rules in the unit relations set
	### uncomment for reactivation
	#changed = True
	#while changed :
		#ur = unitrelation.copy()
		##changed = False
		#for key, units in unitrelation.items() :
			#for unitlabel in units :
				#if unitlabel in unitrelation.keys() :
					#ur[key] += unitrelation[unitlabel]
					#ur[key] = list(set(ur[key]))
		#if cmpstrdict (ur, unitrelation) :
			#changed = False
		#unitrelation = ur
	grammar.unitrelation = unitrelation
	return grammar

def cmpstrdict (d1, d2) :
	for k1, l1 in d1.items() :
		if not k1 in d2.keys() :
			return False
		if len(list(set(l1) - set(d2[k1]))) != 0 :
			return False
	return True

"""
cartesian product between activated production rules in matrix
to see if their combination yields a registred production rule
"""
def cartesianprod (A, B) :
	AB = []
	if A == [] :
		return []
	if B ==  [] :
		return []
	for a in A :
		for b in B :
			AB.append ([a, b])
	return AB

