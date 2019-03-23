from parselib.lexlib import Tokenizer
from parselib.normoperators import *
from parselib.generaloperators import *

from collections import OrderedDict as odict
import pickle, random, json

class Grammar :
	def __init__ (self) :
		self.production_rules = odict()
		self.labels = odict()
		self.keeper = odict()
		self.unitrelation = odict()
		self.importation = []
		self.tokens = list()

	def makegrammar (self, tokenizedgrammar, grammartokens) :
		"""parses a list of tokens in a grammar
		
		Parameters
		----------
		tokenizedgrammar : list(Token)
			list of tokens represented by the lexed grammar
			
		grammartokens : list(Token)
			list of tokens representing the lexed grammar
		"""
		ngp = SequentialParser (tokenizedgrammar, grammartokens) #ngp for naive grammar parser

		ngp.parse () 

		self.production_rules = ngp.production_rules
		self.tokens = ngp.tokens
		self.labels = ngp.labels
		self.keeper = ngp.keeper
		self.importation = ngp.importation
		self = eliminatedoubles (self)

		gramtest = checkproductionrules(self.production_rules) #is fuckedup with the excl add
		return gramtest

	def save (self, filename) :
		"""save parsed grammar in pickle file"""
		serialFile = open (filename, "wb")
		pickle.dump (self.production_rules, serialFile)
		pickle.dump (self.unitrelation, serialFile)
		pickle.dump (self.labels, serialFile)
		pickle.dump (self.keeper, serialFile)
		pickle.dump (self.tokens, serialFile)
		serialFile.close()
	def load (self, filename) :
		"""load grammar from pickle file"""
		serialFile = open (filename, "rb")
		self.production_rules = pickle.load (serialFile)
		self.unitrelation = pickle.load (serialFile)
		self.labels = pickle.load (serialFile)
		self.keeper = pickle.load (serialFile)
		self.tokens = pickle.load (serialFile)
		serialFile.close()

	#def generatestructs (self) :
		#"""Return str containing pycode describing language datastructure
		#"""
		#for key, val in self.keeper.items() :
			#structname = key.capitalize()
			#components=", ".join(
				#[
					#str(
						#v.val if type(v) != str else v
					#) for v in set(val)
				#]
			#)
			#structs[structname] = namedtuple(key, components)
		#return structs

	def __str__ (self) :
		"""Screaming results for debug resons
		"""
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

		text_rule += "STRUCT = [\n{}\n]\n\n".format(
			"".join([
				"\t{} : {{\n\t\t{}\n\t}}\n".format (
					key, ", \n\t\t".join(
						[
							str(
								v.val if type(v) != str else v
							) for v in val
						]
					)
				) for key, val in self.keeper.items()
			])
		)

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
			
			# SPECIAL OPERATORS
			('(\_\_list\_\_|\[\])',			'LIST'),
			('!',							'EXCL'),
			('\%import \".*\"',				'IMPORT'),
			
			('\(\".*\"\)',					'REGEX'),
			('(\->|\=)',					'EQUAL'),
			#('\,',							'COMMA'),
			('\|',							'OR'),
			('\(',							'LPAR'),
			('\)',							'RPAR'),
			#('\[',							'LCRCH'),
			#('\]',							'RCRCH'),

			#OPERANDS
			(label+'?[a-zA-Z0-9_]\w*\.',		'TERMINAL'),
			(label+'?[a-zA-Z0-9_]\w*',			'NONTERMINAL'),
		]
		
		AXIOM = r'AXIOM EQUAL (NONTERMINAL|GENERATOR)'
		LSIDE = r'NONTERMINAL EQUAL'
		RSIDE = r'EXCL|LIST|TERMINAL|NONTERMINAL|EMPTY'
		IMPORT= r"IMPORT"
		TOKEN = r'TERMINAL REGEX'
		
		self.genericgrammarprodrules = [
			('LINECOMMENT',	'LINECOMMENT'),
			(AXIOM,			'AXIOM'),
			(TOKEN,			'TOKEN'),
			(IMPORT,		'IMPORT'),

			(LSIDE,			'LSIDE'),
			(RSIDE,			'RSIDE'),

			('OR',			'OR'),
			#('COMMA',		'COMMA'),
			('LCRCH',		'LCRCH'),
			('RCRCH',		'RCRCH'),
		]

	def parse (self, txt_grammar="", verbose=False) :
		"""lex a grammar from textual form to tokenized
		
		Parameters
		----------
		txt_grammar : str
			raw grammar source code
		
		verbose : bool
			True to make it talk. False by default
		"""

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

		if (result == []) :
			if verbose : print (grammar)
		else :
			if verbose : print (result)
		return grammar


"""
TODO : 
	parse list() operator in a production rule
"""
class SequentialParser :
	def __init__ (self, grammar, parsedtokens) :
		self.production_rules = odict()
		self.labels = odict()
		self.keeper = odict({'all' : []})
		self.tokens = list()
		
		self.grammar = grammar
		self.parsedtokens = parsedtokens
		
		self.importation = []
		
		self.axiomflag = True
		
		self.i, self.j, self.current_rule = 0, 0, ""

	def parse (self) :
		while self.stillparsing() :
			self.checkaxiom ()
			self.checkimport ()

			self.checkleftside()
			self.checkrightside()

			self.checkoperators ()
			self.checkfortoken()

	def stillparsing (self) :
		return self.i < len(self.grammar)

	def checkimport (self) :
		"""just reads the filename to import (if any)
		grammar doesn't support importation yet
		"""
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "IMPORT" :
			self.importation.append(self.parsedtokens[j].val.split("%import")[1].strip()[1:-1])
			j+=1
			i+=1
		self.i, self.j = i, j
			
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
			if self.parsedtokens[j].type == "LIST" :
				thisnode = Token ("NONTERMINAL", self.current_rule, 0)
				eps = Token("EMPTY", '""', 0)
				self.production_rules[self.current_rule][-1] = [thisnode, thisnode]
				self.production_rules[self.current_rule].append([eps])
				j+=1
				i+=1
				continue

			if self.parsedtokens[j].type == "EXCL" :

				if self.current_rule in self.keeper.keys() :
					self.keeper[self.current_rule].append(self.parsedtokens[j+1])
				else :
					self.keeper[self.current_rule] = [self.parsedtokens[j+1]]

				if not self.parsedtokens[j+1].val in self.keeper["all"] :
					if self.parsedtokens[j+1].type == "TERMINAL" :
						self.keeper["all"].append(self.parsedtokens[j+1].val[:-1])
					else :
						self.keeper["all"].append(self.parsedtokens[j+1].val)
				j += 1
				i += 1
				continue

			if self.parsedtokens[j].type == "TERMINAL" :
				self.parsedtokens[j].val = self.parsedtokens[j].val[:-1] #eliminate . at terminals

			if self.parsedtokens[j].val.find('=') != -1 :

				label, operand= self.parsedtokens[j].val.split('=', 1)
				self.parsedtokens[j].val = operand
				if self.current_rule in self.labels.keys() :
					self.labels[self.current_rule].update({operand : label})
				else :
					self.labels[self.current_rule] = {operand : label}

				if self.current_rule in self.keeper.keys() :
					self.keeper[self.current_rule].append(label)
				else :
					self.keeper[self.current_rule] = [label]
				if not label in self.keeper["all"] :
					self.keeper["all"].append(label)

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





