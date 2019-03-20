from parselib.lexlib import Tokenizer
from parselib.normoperators import *
from parselib.generaloperators import *

from collections import OrderedDict as odict
import pickle, random, json

class Grammar :
	def __init__ (self) :
		self.production_rules = odict()
		self.labels = odict()
		self.unitrelation = odict()
		self.tokens = list()

	def makegrammar (self, tokenizedgrammar, grammartokens) :
		ngp = NaiveParser (tokenizedgrammar, grammartokens) #ngp for naive grammar parser

		while ngp.stillparsing() :
			ngp.checkaxiom ()
			ngp.checkleftside()
			ngp.checkrightside()
			
			ngp.checkoperators ()
			ngp.checkfortoken()
			
		self.production_rules = ngp.production_rules
		self.tokens = ngp.tokens
		self.labels = ngp.labels

		self = eliminatedoubles (self)

		gramtest = checkproductionrules(self.production_rules)
		return gramtest

	def save (self, filename) :
		serialFile = open (filename, "wb")
		pickle.dump (self.production_rules, serialFile)
		pickle.dump (self.unitrelation, serialFile)
		pickle.dump (self.labels, serialFile)
		pickle.dump (self.tokens, serialFile)
		serialFile.close()
	def load (self, filename) :
		serialFile = open (filename, "rb")
		self.production_rules = pickle.load (serialFile)
		self.unitrelation = pickle.load (serialFile)
		self.labels = pickle.load (serialFile)
		self.tokens = pickle.load (serialFile)
		serialFile.close()

	def __str__ (self) :
		text_rule = ""
		
		for key, rules in self.production_rules.items() :
			text_rule += "\nRULE " + key + " = [\n\t"
			rule_in_a_line = []
			for rule in rules :
				#rule_in_a_line.append(" + ".join([r.val+"("+r.type+")" for r in rule]))
				rule_in_a_line.append(" + ".join([r.__str__() for r in rule]))
			text_rule += "\n\t".join(rule_in_a_line) + "\n]"
		text_rule += "\n\n"
		
		text_rule += "LABELS = " + json.dumps (self.labels, indent=2) + '\n\n'
		
		for regex, label in self.tokens :
			text_rule += "TOKEN " + label + " = regex('" + regex + "')\n"

		return text_rule

class GenericGrammarParser :
	def __init__ (self) :
		label="([a-zA-Z_]\w*=)"
		self.grammartokens = [
			#KEYWORDS
			('(//|\;).*',					'LINECOMMENT'),
			('\'\'|\"\"',					'EMPTY'),
			('AXIOM',						'AXIOM'),
			
			# OPERATORS
			#experimental operators
			('list',						'LIST'),
			('!',							'EXCL'),
			
			
			('\(\".*\"\)',					'REGEX'),
			('(\->|\=)',					'EQUAL'),
			#('\,',							'COMMA'),
			('\|',							'OR'),
			('\(',							'LPAR'),
			('\)',							'RPAR'),
			#('\[',							'LCRCH'),
			#('\]',							'RCRCH'),

			#OPERANDS
			(label+'?[a-zA-Z_]\w*\.',		'TERMINAL'),
			(label+'?[a-zA-Z_]\w*',			'NONTERMINAL'),
		]
		
		AXIOM = r'AXIOM EQUAL (NONTERMINAL|GENERATOR)'
		LSIDE = r'NONTERMINAL EQUAL'
		RSIDE = r'!|TERMINAL|NONTERMINAL|EMPTY'
		TOKEN = r'TERMINAL REGEX'
		
		self.genericgrammarprodrules = [
			('LINECOMMENT',	'LINECOMMENT'),
			(AXIOM,			'AXIOM'),
			(TOKEN,			'TOKEN'),

			(LSIDE,			'LSIDE'),
			(RSIDE,			'RSIDE'),

			('OR',			'OR'),
			#('COMMA',		'COMMA'),
			('LCRCH',		'LCRCH'),
			('RCRCH',		'RCRCH'),
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

		##make production rules
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
	

"""
TODO : 
	parse list() operator in a production rule
"""
class NaiveParser :
	def __init__ (self, grammar, parsedtokens) :
		self.production_rules = odict()
		self.labels = odict()
		self.tokens = list()
		
		self.grammar = grammar
		self.parsedtokens = parsedtokens
		
		self.axiomflag = True
		
		self.i, self.j, self.current_rule = 0, 0, ""
	
	def stillparsing (self) :
		return self.i < len(self.grammar)
	
	def checkaxiom (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "AXIOM" and self.axiomflag :
			axiom = self.parsedtokens[j+2]
			self.production_rules["AXIOM"] = [[axiom]]
			self.axiomflag = False
			i += 1
			j += 3
		self.i, self.j = i, j

	def checkleftside (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "LSIDE" :
			self.current_rule = self.parsedtokens[j].val
			if not self.current_rule in self.production_rules.keys() :
				self.production_rules[self.current_rule] = [[]]
			i += 1
			j += 2
		self.i, self.j = i, j
	
	def checkoperators (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if (self.grammar[i].type == "OR" and self.parsedtokens[j].type == "OR") :
			self.production_rules[self.current_rule].append([])
			j += 1
			i += 1
		if self.grammar[i].type == "LINECOMMENT" and self.parsedtokens[j].type == "LINECOMMENT" :
			j += 1
			i += 1
		self.i, self.j = i, j

	def checkrightside (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		while self.grammar[i].type == "RSIDE" :
			if self.parsedtokens[j].type == "TERMINAL" :
				self.parsedtokens[j].val = self.parsedtokens[j].val[:-1] #eliminate . at terminals
			if self.parsedtokens[j].val.find('=') != -1 :
				label, operand= self.parsedtokens[j].val.split('=', 1)
				self.parsedtokens[j].val = operand
				self.parsedtokens[j].label = label
				self.parsedtokens[j].keep = True
				if self.current_rule in self.labels.keys() :
					self.labels[self.current_rule].append({operand : label})
				else :
					self.labels[self.current_rule] = [{operand : label}]
			self.production_rules[self.current_rule][-1].append(self.parsedtokens[j])			
			i += 1
			j += 1
		self.i, self.j = i, j

	def checkfortoken (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "TOKEN" :
			label = self.parsedtokens[j].val[:-1] #eliminate the dot
			regex = self.parsedtokens[j+1].val[2:-2] #eliminate the ("...")
			self.tokens.append((regex, label)) 
			i += 1
			j += 2
		self.i, self.j = i, j





