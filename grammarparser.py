from lexlib import Lexer, LexerError, Token
from ChomskyNormalizer import *
from collections import OrderedDict as odict

import pickle, random

#parse grammar source code to tokens
class Tokenizer :
	def __init__ (self, tokens_re_list) :
		self.tokens_re_list = tokens_re_list
		self.tokenizedgrammar = None
	
	def parse (self, source) :
		lx = Lexer(self.tokens_re_list, skip_whitespace=True)
		lx.input(source)

		try:
			tokenizedgrammar = []
			for tok in lx.tokens():
				tokenizedgrammar.append(tok)
		except LexerError as err:
			print('LexerError at position %s' % err.pos)
		self.tokenizedgrammar = tokenizedgrammar

	def __str__ (self) :
		s = ""
		for token in self.tokenizedgrammar :
			s += token.__str__() + "\n"
		return s

class ProductionRulesGenerator :
	def __init__ (self) :
		self.production_rules = None
		pass
	
	def makeprodrules (self, parsedgrammar, lexgrammar) :
		self.production_rules = odict()
		self.axiomflag = True
		i, j = 0, 0
		current_rule = ""
		while self._checkparsingend(i, parsedgrammar) :
			i, j, current_rule = self._checkaxiom (i, parsedgrammar, j, lexgrammar, current_rule)
			i, j, current_rule = self._checkleftside (i, parsedgrammar, j, lexgrammar, current_rule)
			i, j, current_rule = self._checkoperators (i, parsedgrammar, j, lexgrammar, current_rule)
			i, j, current_rule = self._checkrightside (i, parsedgrammar, j, lexgrammar, current_rule)
		gramtest = self.checkproductionrules()
		return gramtest
	
	def checkproductionrules (self) :
		keys = ["AXIOM"]
		for key, rules in self.production_rules.items() :
			for rule in rules :
				for operand in rule :
					if (not operand.val in keys) and (operand.type == "NONTERMINAL") :
						keys.append(operand.val)				
		if set(self.production_rules.keys()) == set(keys) :
			return True, list()
		else :
			return False, list(set(self.production_rules.keys())-set(keys))
	
	def _checkparsingend (self, i, lst) :
		return i < len (lst)

	def _checkaxiom (self, i, grammar, j, tokens, current_rule) :
		if not self._checkparsingend (i, grammar) :
			return (i, j, current_rule)
		if grammar[i].type == "AXIOM" and self.axiomflag :
			self.production_rules["AXIOM"] = [[tokens[j+2]]]
			self.axiomflag = False
			i += 1
			j += 3
		return (i, j, current_rule)

	def _checkleftside (self, i, grammar, j, tokens, current_rule) :
		if not self._checkparsingend (i, grammar) :
			return (i, j, current_rule)
		if grammar[i].type == "LSIDE" :
			current_rule = tokens[j].val
			if not current_rule in self.production_rules.keys() :
				self.production_rules[current_rule] = [[]]
			i += 1
			j += 2
		return (i, j, current_rule)

	def _checkoperators (self, i, grammar, j, tokens, current_rule) :
		if not self._checkparsingend (i, grammar) :
			return (i, j, current_rule)
		if (grammar[i].type == "OR" and tokens[j].type == "OR") :
			self.production_rules[current_rule].append([])
			j += 1
			i += 1
		if (grammar[i].type == "PLUS" and tokens[j].type == "PLUS") :
			j += 1
			i += 1
		return (i, j, current_rule)

	def _checkrightside (self, i, grammar, j, tokens, current_rule) :
		if not self._checkparsingend (i, grammar) :
			return (i, j, current_rule)
		if grammar[i].type == "RSIDE" :
			if tokens[j].type == "TERMINAL" :
				tokens[j].val = tokens[j].val[:-4] #eliminate .tok
			self.production_rules[current_rule][-1].append(tokens[j])			
			i += 1
			j += 1
		return (i, j, current_rule)

	def __str__ (self) :
		text_rule = ""
		
		for key, rules in self.production_rules.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in rules :
				#text_rule += str(type(rule))
				rule_in_a_line.append(" + ".join([r.val+"."+r.type+"."+str(r.pos) for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"

		return text_rule

	def normalizegrammar (self) :
		production_rules = self.production_rules
		cnf = ChomskyNormalForm (production_rules)
		self.production_rules = cnf.getnormalform()

	def linearizegrammar(self) :
		production_rules = self.production_rules
		changed = True
		while changed :
			gr = GrammarLinearizer (production_rules)
			production_rules, changed = gr.linearizegrammar()
		self.production_rules = production_rules

	def save (self, filename) :
		serialFile = open (filename, "wb")
		pickle.dump (self.production_rules, serialFile)
		serialFile.close()
	def load (self, filename) :
		serialFile = open (filename, "rb")
		self.production_rules = pickle.load (serialFile)
		serialFile.close()


class GrammarLinearizer :
	def __init__ (self, production_rules) :
		self.production_rules = production_rules
		self.regularized_production_rules = None

	def linearizegrammar (self) :
		self.regularized_production_rules = odict()
		changed = False
		for key, rules in self.production_rules.items() :
			keyprefix = key
			self.regularized_production_rules[keyprefix] = []
			for rule in rules :
				if len(rule) == 1 : #single operand
					self.regularized_production_rules[keyprefix].append([rule[0]])
				elif len(rule) == 2 : # 2 operands whatever they are
					self.regularized_production_rules[keyprefix].append(rule)
				elif rule[0].type == "TERMINAL" : #regularize from left
					self.leftregularizerule (keyprefix, rule)
					changed = True
				elif rule[-1].type == "TERMINAL" : #regularize from right
					self.rightregularizerule (keyprefix, rule)
					changed = True
				elif rule[0].type == rule[-1].type : #divide expression for regularization purposes
					self.divideexpression (keyprefix, rule)
					changed = True
		return self.regularized_production_rules, changed

	def __str__ (self) :
		text_rule = ""
		
		for key, rules in self.regularized_production_rules.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in rules :
				#text_rule += str(type(rule))
				rule_in_a_line.append(" + ".join([r.val+"."+r.type+"."+str(r.pos) for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"

		return text_rule


	def divideexpression (self, keyprefix, rule) :
		lenmax = random.sample (range(1, len(rule)-1), 1)[0]
		rule_id = keyprefix + "-".join([r.val for r in rule[:lenmax]])
		if rule_id in self.regularized_production_rules.keys() :
			return 
		tok1 = Token ("NONTERMINAL", rule_id, rule[0].pos)
		self.regularized_production_rules[rule_id] = [rule[:lenmax]]
		
		rule_id = keyprefix + "-".join([r.val for r in rule[lenmax:]])
		if rule_id in self.regularized_production_rules.keys() :
			return 
		self.regularized_production_rules[rule_id] = [rule[lenmax:]]
		tok2 = Token ("NONTERMINAL", rule_id, rule[lenmax].pos)

		self.regularized_production_rules[keyprefix].append([tok1, tok2])
		
		gr = GrammarLinearizer (self.regularized_production_rules) 
		self.regularized_production_rules = gr.regularizegrammar()
	
	def leftregularizerule (self, keyprefix, rule) :
		rule_id = keyprefix + "-".join([rule[i].val for i in range(1, len(rule))])
		if rule_id in self.regularized_production_rules.keys() :
			return 
		else :
			self.regularized_production_rules[keyprefix].append([
				rule[0],
				Token ("NONTERMINAL", rule_id, rule[1].pos),
			])
			self.regularized_production_rules[rule_id] = [rule[1:]]

	def rightregularizerule (self, keyprefix, rule) :
		rule_id = keyprefix + "-".join([rule[i].val for i in range(0, len(rule)-1)])
		if rule_id in self.regularized_production_rules.keys() :
			return 
		else :
			self.regularized_production_rules[keyprefix].append([
				Token ("NONTERMINAL", rule_id, rule[-2].pos),
				rule[-1], 
			])
			self.regularized_production_rules[rule_id] = [rule[:-1]]


class GenericGrammarParser :
	def __init__ (self, txt_grammar="") :
		self.txt_grammar = txt_grammar
		
	def parse (self, verbose=False) :
		tok, grm = self.tokenize(verbose)
		self.getproductions (tok, grm, verbose)
	
	def tokenize (self, verbose=False) :
		grammartokens = [
			('AXIOM',				'AXIOM'),
			('[a-zA-Z_]\w*\.(tok|gen)',	'TERMINAL'),
			('[a-zA-Z_]\w*',		'NONTERMINAL'),
			('\:=',					'EQUAL'),
			('\+',					'PLUS'),
			('\|',					'OR'),
			('\'\'|\"\"',			'EMPTY'),
		]
		
		AXIOM = r'AXIOM EQUAL NONTERMINAL'
		LSIDE = r'NONTERMINAL EQUAL'
		RSIDE = r'(TERMINAL|NONTERMINAL)+|EMPTY'
		OR, PLUS = r'OR', r'PLUS'
		genericgrammarprodrules = [
			(AXIOM,		'AXIOM'),
			(LSIDE,		'LSIDE'),
			(RSIDE,		'RSIDE'),
			(OR,		'OR'),
			(PLUS,		'PLUS'),
		]

		#lex language => tokenized grammar
		tokenizer = Tokenizer (grammartokens)
		tokenizer.parse (self.txt_grammar)
		if verbose : print(tokenizer)

		#lex tokenized grammar => tokenized language
		gram = Tokenizer (genericgrammarprodrules)
		txtok = self._transformtosource (tokenizer.tokenizedgrammar)
		gram.parse (txtok)
		if verbose : print(gram)
		
		return tokenizer, gram

	def getproductions (self, tokenizer, gram, verbose=False) :
		#make production rules
		prodrulesgen = ProductionRulesGenerator ()
		result = prodrulesgen.makeprodrules (
			gram.tokenizedgrammar,
			tokenizer.tokenizedgrammar,
		)

		if (result == (True,[])) :
			#prodrulesgen.linearizegrammar()
			prodrulesgen.normalizegrammar()
			if verbose : print (prodrulesgen)
		else :
			if verbose : print (result)
		return prodrulesgen

	def _transformtosource (self, tokenizedgrammar) :
		source = ""
		for token in tokenizedgrammar :
			source += token.type + " "
		return source

