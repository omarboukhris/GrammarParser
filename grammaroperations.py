

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

def checkaxiom (production_rules, i, grammar, j, tokens, current_rule, axiomflag) :
	if not i < len(grammar) :
		return (i, j, current_rule)
	if grammar[i].type == "AXIOM" and axiomflag :
		production_rules["AXIOM"] = [[tokens[j+2]]]
		axiomflag = False
		i += 1
		j += 3
	return (production_rules, i, j, current_rule, axiomflag)

def checkleftside (production_rules, i, grammar, j, tokens, current_rule) :
	if not i < len(grammar) :
		return (i, j, current_rule)
	if grammar[i].type == "LSIDE" :
		current_rule = tokens[j].val
		if not current_rule in production_rules.keys() :
			production_rules[current_rule] = [[]]
		i += 1
		j += 2
	return (production_rules, i, j, current_rule)

def checkoperators (production_rules, i, grammar, j, tokens, current_rule) :
	if not i < len(grammar) :
		return (i, j, current_rule)
	if (grammar[i].type == "OR" and tokens[j].type == "OR") :
		production_rules[current_rule].append([])
		j += 1
		i += 1
	if (grammar[i].type == "PLUS" and tokens[j].type == "PLUS") :
		j += 1
		i += 1
	return (production_rules, i, j, current_rule)

def checkrightside (production_rules, i, grammar, j, tokens, current_rule) :
	if not i < len(grammar) :
		return (i, j, current_rule)
	if grammar[i].type == "RSIDE" :
		if tokens[j].type == "TERMINAL" :
			tokens[j].val = tokens[j].val[:-4] #eliminate .tok
		production_rules[current_rule][-1].append(tokens[j])			
		i += 1
		j += 1
	return (production_rules, i, j, current_rule)

def transformtosource (tokenizedgrammar) :
	source = ""
	for token in tokenizedgrammar :
		source += token.type + " "
	return source


