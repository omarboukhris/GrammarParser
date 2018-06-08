from lexlib import Tokenizer
from ChomskyNormalizer import *
from grammaroperations import *

from collections import OrderedDict as odict
import pickle, random

class Grammar :
	def __init__ (self) :
		self.production_rules = None
		self.langtokens = None

	def makegrammar (self, parsedgrammar, lexgrammar) :
		self.production_rules = odict()
		self.langtokens = odict()
		self.axiomflag = True
		i, j = 0, 0
		current_rule = ""
		while i < len(parsedgrammar) :
			self.production_rules, i, j, current_rule, self.axiomflag = checkaxiom (
				self.production_rules, i, parsedgrammar, j, lexgrammar, current_rule, self.axiomflag
			)
			self.production_rules, i, j, current_rule = checkleftside (self.production_rules, i, parsedgrammar, j, lexgrammar, current_rule)
			self.production_rules, i, j, current_rule = checkoperators(self.production_rules, i, parsedgrammar, j, lexgrammar, current_rule)
			self.production_rules, i, j, current_rule = checkrightside(self.production_rules, i, parsedgrammar, j, lexgrammar, current_rule)
			self.langtokens, i, j, current_rule = checkfortoken (self.langtokens, i, parsedgrammar, j, lexgrammar, current_rule)
		gramtest = checkproductionrules(self.production_rules)
		self.langtokens = list(self.langtokens.items ())
		return gramtest

	def save (self, filename) :
		serialFile = open (filename, "wb")
		pickle.dump (self.production_rules, serialFile)
		pickle.dump (self.langtokens, serialFile)
		serialFile.close()
	def load (self, filename) :
		serialFile = open (filename, "rb")
		self.production_rules = pickle.load (serialFile)
		self.langtokens = pickle.load (serialFile)
		serialFile.close()

	def __str__ (self) :
		text_rule = ""
		
		for key, rules in self.production_rules.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in rules :
				rule_in_a_line.append(" + ".join([r.val+"("+r.type+")" for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"

		for key, rule in self.langtokens :
			text_rule += "\nRULE " + key + " = [ " + rule[0] + " ]\n"

		return text_rule

class GenericGrammarParser :
	def __init__ (self) :
		self.grammartokens = [
			('\;.*\n',						'LINECOMMENT'),
			('\'\'|\"\"',					'EMPTY'),
			('AXIOM',						'AXIOM'),
			('[a-zA-Z_]\w*\.(gen)?',		'TERMINAL'),
			('[a-zA-Z_]\w*',				'NONTERMINAL'),
			('\->',							'EQUAL'),
			('\+',							'PLUS'),
			('\|',							'OR'),
			#('.*',							'REGEX'),
		]
		
		AXIOM = r'AXIOM EQUAL NONTERMINAL'
		LSIDE = r'NONTERMINAL EQUAL'
		RSIDE = r'(TERMINAL|NONTERMINAL)+|EMPTY'
		TOKEN = r'TERMINAL EQUAL REGEX'
		OR, PLUS, LINECOMMENT = r'OR', r'PLUS', r'LINECOMMENT'
		self.genericgrammarprodrules = [
			(LINECOMMENT,	'LINECOMMENT'),
			(AXIOM,			'AXIOM'),
			(TOKEN,			'TOKEN'),
			(LSIDE,			'LSIDE'),
			(RSIDE,			'RSIDE'),
			(OR,			'OR'),
			(PLUS,			'PLUS'),
		]

	def parse (self, txt_grammar="", verbose=False) :

		#lex language => tokenized grammar
		lang = Tokenizer (self.grammartokens)
		#lex tokenized grammar => tokenized language
		gram = Tokenizer (self.genericgrammarprodrules)

		lang.parse (txt_grammar)
		if verbose : print(lang)

		txtok = transformtosource (lang.tokenized)
		gram.parse (txtok)
		if verbose : print(gram)

		#make production rules
		grammar = Grammar ()
		result = grammar.makegrammar (
			gram.tokenized,
			lang.tokenized,
		)

		if (result == (True,[])) :
			if verbose : print (grammar)
		else :
			if verbose : print (result)
		return grammar
	
