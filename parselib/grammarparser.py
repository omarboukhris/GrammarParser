from parselib.lexlib import Tokenizer
from parselib.ChomskyNormalizer import *
from parselib.grammaroperations import *

from collections import OrderedDict as odict
import pickle, random

class Grammar :
	def __init__ (self) :
		self.production_rules = odict()
		self.generator_rules = odict()
		self.generator_labels = odict()
		self.langtokens = list()

	def makegrammar (self, parsedgrammar, lexgrammar) :
		ngp = NaiveParser (parsedgrammar, lexgrammar) #ngp for naive grammar parser

		while ngp.stillparsing() :
			ngp.checkaxiom ()
			ngp.checkleftside()
			ngp.checkrightside()
			
			ngp.checkleftsidelab()
			ngp.checkrightsidelab()
			ngp.checkleftsidegen()
			ngp.checkrightsidegen()
			
			ngp.checkoperators ()
			ngp.checkfortoken()
			
		self.production_rules = ngp.production_rules
		self.generator_rules = ngp.generator_rules
		self.generator_labels = ngp.generator_labels
		self.langtokens = ngp.langtokens

		gramtest = checkproductionrules(self.production_rules)
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
		text_rule += "\n\n"
		
		for key, labels in self.generator_labels.items() :
			text_rule += "GENLABELS " + key + " = " + ", ".join(labels) + "\n"
		text_rule += "\n"
		
		for key, rules in self.generator_rules.items() :
			text_rule += "GENERATOR " + key + " = [\n" 
			for lilkey, rule in rules.items() :
				text_rule += "\t'" + lilkey + "' : " + " + ".join([r.val+"("+r.type+")" for r in rule]) + "\n"
			text_rule += "]\n"
		text_rule += "\n"
		
		for regex, label in self.langtokens :
			text_rule += "TOKEN " + label + " = regex('" + regex + "')\n"

		return text_rule

class GenericGrammarParser :
	def __init__ (self) :
		self.grammartokens = [
			#KEYWORDS
			('(//|\;).*',					'LINECOMMENT'),
			('\'\'|\"\"',					'EMPTY'),
			('AXIOM',						'AXIOM'),
			
			# OPERATORS
			#experimental operators
			('\[\"[a-zA-Z_]\w*\"\]',		'KEYOP'),
			('list\([a-zA-Z_]\w*\.g(en)?\)','LIST'),
			('str\([a-zA-Z_]\w*\)',			'STR'),
			
			('\(\".*\"\)',					'REGEX'),
			('(\->|\=)',					'EQUAL'),
			#('\,',							'COMMA'),
			('\|',							'OR'),
			('\(',							'LPAR'),
			('\)',							'RPAR'),
			#('\[',							'LCRCH'),
			#('\]',							'RCRCH'),

			#OPERANDS
			#generator operands are prioritarized to avoid eventual mislabeling
			('[a-zA-Z_]\w*\.g(en)?',		'GENERATOR'),
			('[a-zA-Z_]\w*\.l(ab)?',		'LABELATOR'),
			('\"[a-zA-Z_]\w*\"(\,)?',		'LABEL'),

			('[a-zA-Z_]\w*\.',				'TERMINAL'),
			('[a-zA-Z_]\w*',				'NONTERMINAL'),
		]
		
		AXIOM = r'AXIOM EQUAL (NONTERMINAL|GENERATOR)'
		LSIDE = r'NONTERMINAL EQUAL'
		RSIDE = r'TERMINAL|NONTERMINAL|EMPTY'
		TOKEN = r'TERMINAL REGEX'
		
		#experimental rules
		LSGEN = r'GENERATOR EQUAL |GENERATOR KEYOP EQUAL'
		RSGEN = r'NONTERMINAL LPAR (NONTERMINAL|GENERATOR|LIST|STR) RPAR'
		
		LSLAB = r'LABELATOR EQUAL'
		RSLAB = r'LABEL'
		
		self.genericgrammarprodrules = [
			('LINECOMMENT',	'LINECOMMENT'),
			(AXIOM,			'AXIOM'),
			(TOKEN,			'TOKEN'),

			(LSGEN,			'LSGEN'),
			(RSGEN,			'RSGEN'),

			(LSLAB,			'LSLAB'),
			(RSLAB,			'RSLAB'),

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
	


class NaiveParser :
	def __init__ (self, grammar, tokens) :
		self.production_rules = odict()
		self.generator_rules = odict()
		self.generator_labels = odict()
		self.langtokens = list()

		self.grammar = grammar
		self.tokens = tokens
		
		self.axiomflag = True
		
		self.keyop = ""
		
		self.i, self.j, self.current_rule = 0, 0, ""
	
	def stillparsing (self) :
		return self.i < len(self.grammar)
	
	def checkaxiom (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "AXIOM" and self.axiomflag :
			self.production_rules["AXIOM"] = [[self.tokens[j+2]]]
			self.axiomflag = False
			i += 1
			j += 3
		self.i, self.j = i, j

	def checkleftside (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "LSIDE" :
			self.current_rule = self.tokens[j].val
			if not self.current_rule in self.production_rules.keys() :
				self.production_rules[self.current_rule] = [[]]
			i += 1
			j += 2
		self.i, self.j = i, j
	
	def checkoperators (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if (self.grammar[i].type == "OR" and self.tokens[j].type == "OR") :
			self.production_rules[self.current_rule].append([])
			j += 1
			i += 1
		if self.grammar[i].type == "LINECOMMENT" and self.tokens[j].type == "LINECOMMENT" :
			j += 1
			i += 1
		self.i, self.j = i, j

	def checkrightside (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		while self.grammar[i].type == "RSIDE" :
			if self.tokens[j].type == "TERMINAL" :
				self.tokens[j].val = self.tokens[j].val[:-1] #eliminate . at terminals
			self.production_rules[self.current_rule][-1].append(self.tokens[j])			
			i += 1
			j += 1
		self.i, self.j = i, j

	def checkfortoken (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "TOKEN" :
			label = self.tokens[j].val[:-1] #eliminate the dot
			regex = self.tokens[j+1].val[2:-2] #eliminate the ("...")
			self.langtokens.append((regex, label)) 
			i += 1
			j += 2
		self.i, self.j = i, j
	
	def checkleftsidelab  (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "LSLAB" :
			self.current_rule = self.tokens[j].val.split(".")[0] #remove .lab
			self.generator_labels[self.current_rule] = []
			j+= 2
			i+= 1
		self.i, self.j = i, j

	def checkrightsidelab (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		while self.grammar[i].type == "RSLAB" :
			label = self.tokens[j].val.split(',')[0][1:-1] #eliminate comma if any and quotes
			self.generator_labels[self.current_rule].append (label)
			#print (label)
			i += 1
			j += 1
		self.i, self.j = i, j

	def checkleftsidegen (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "LSGEN" :
			self.current_rule = self.tokens[j].val.split(".")[0] #remove .g(en)
			if not self.current_rule in self.generator_rules.keys() :
				self.generator_rules[self.current_rule] = odict()

			if self.tokens[j+1].type == "KEYOP" : #if bifurcated rule
				self.keyop = self.tokens[j+1].val[2:-2]
				j += 3
			else : #if unique rule
				self.keyop = "all"
				j+= 2

			self.generator_rules[self.current_rule][self.keyop] = []
			i+= 1
		self.i, self.j = i, j

	def checkrightsidegen (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		while self.grammar[i].type in ["RSGEN", "RSIDE"] :
			if self.grammar[i].type == "RSGEN" :
				label = self.tokens[j].val
				#print (label, self.current_rule)
				#print (self.generator_labels)
				if label in self.generator_labels[self.current_rule] :
					#rule is Token(val, type, pos)
					rule = self.tokens[j+2]
					#RSGEN catches a NONTERMINAL even if it represents a TOKEN
					#add a data type to recognize them, ex : LABELED_DATA or smth
					rule.type = "LABELED_DATA"
					#if self.keyop == "all" :
						#self.generator_rules[self.current_rule]['all'].append ( rule ) 
					#else :
					self.generator_rules[self.current_rule][self.keyop].append ( rule )
					j += 4
				#print (self.generator_rules)
			else :
				self.generator_rules[self.current_rule]['all'].append( self.tokens[j] ) 
				j += 1
			i += 1
		self.i, self.j = i, j


