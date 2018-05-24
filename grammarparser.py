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

class GenericGrammarParser :
	def __init__ (self, txt_grammar="") :
		self.txt_grammar = txt_grammar
		
	def parse (self, verbose=False) :
		tok, grm = self.tokenize(verbose)
		return self.getproductions (tok, grm, verbose)
	
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

