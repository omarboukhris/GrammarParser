from parselib.lexlib import Tokenizer
from parselib.normoperators import *
from parselib.generaloperators import *

from collections import OrderedDict as odict
import pickle, random

class Grammar :
	def __init__ (self) :
		self.production_rules = odict()
		self.generator_rules = odict()
		self.generator_labels = odict()
		self.unitrelation = odict()
		self.tokens = list()

	def makegrammar (self, tokenizedgrammar, grammartokens) :
		ngp = NaiveParser (tokenizedgrammar, grammartokens) #ngp for naive grammar parser

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
		self.tokens = ngp.tokens

		self = eliminatedoubles (self)

		gramtest = checkproductionrules(self.production_rules)
		return gramtest

	def save (self, filename) :
		serialFile = open (filename, "wb")
		pickle.dump (self.production_rules, serialFile)
		pickle.dump (self.generator_rules, serialFile)
		pickle.dump (self.generator_labels, serialFile)
		pickle.dump (self.unitrelation, serialFile)
		pickle.dump (self.tokens, serialFile)
		serialFile.close()
	def load (self, filename) :
		serialFile = open (filename, "rb")
		self.production_rules = pickle.load (serialFile)
		self.generator_rules = pickle.load (serialFile)
		self.generator_labels = pickle.load (serialFile)
		self.unitrelation = pickle.load (serialFile)
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
		
		for (key, rules), (key, labels) in zip(self.generator_rules.items(), self.generator_labels.items()) :
			text_rule += "GENERATOR " + key + " ( " + ", ".join(labels) + " ) {\n" 
			for lilkey, rule in rules.items() :
				text_rule += "\t'" + lilkey + "' : " + " + ".join([r.__str__() for r in rule]) + "\n"
			text_rule += "}\n"
		text_rule += "\n"
		
		for regex, label in self.tokens :
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
			('list\:[a-zA-Z_]\w*\.g(en)?',	'LIST'),
			#('str\([a-zA-Z_]\w*\)',			'STR'),
			
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
		##..not anymore :p
		LSGEN = r'GENERATOR EQUAL |GENERATOR KEYOP EQUAL'
		RSGEN = r'NONTERMINAL LPAR (TERMINAL|NONTERMINAL|GENERATOR|LIST) RPAR'
		
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
	def __init__ (self, grammar, parsedtokens) :
		self.production_rules = odict()
		self.generator_rules = odict()
		self.generator_labels = odict()
		self.tokens = list()

		self.grammar = grammar
		self.parsedtokens = parsedtokens
		
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
			axiom = self.parsedtokens[j+2]
			#reactivate if needed for test purposes
			#if axiom.type == "GENERATOR" :
				#axiom.type = "NONTERMINAL"
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
	
	def checkleftsidelab  (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "LSLAB" :
			#self.current_rule = self.tokens[j].val.split(".")[0] #remove .lab 
			self.current_rule = self.parsedtokens[j].val.replace (".lab", ".gen") #transf lab -> gen
			self.generator_labels[self.current_rule] = []
			j+= 2
			i+= 1
		self.i, self.j = i, j

	def checkrightsidelab (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		while self.grammar[i].type == "RSLAB" :
			label = self.parsedtokens[j].val.split(',')[0][1:-1] #eliminate comma if any and quotes
			self.generator_labels[self.current_rule].append (label)
			i += 1
			j += 1
		self.i, self.j = i, j

	def checkleftsidegen (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		if self.grammar[i].type == "LSGEN" :
			self.current_rule = self.parsedtokens[j].val.split(".")[0] #remove .g to add .gen
			self.current_rule += ".gen"
			if not self.current_rule in self.generator_rules.keys() :
				self.generator_rules[self.current_rule] = odict()

			if not self.current_rule in self.production_rules.keys() :
				self.production_rules[self.current_rule] = [[]]

			if self.parsedtokens[j+1].type == "KEYOP" : #if bifurcated rule
				self.keyop = self.parsedtokens[j+1].val[2:-2]
				if self.production_rules[self.current_rule] == [[]] :
					self.production_rules[self.current_rule] = []
				self.production_rules[self.current_rule].append([])
				j += 3
			else : #if unique rule
				self.keyop = "all"
				j+= 2

			self.generator_rules[self.current_rule][self.keyop] = []

			i+= 1
		self.i, self.j = i, j
		
	def makelistrule (self, rule) :
		iterated = rule.val.split (":")[1]
		
		genname = "list:" + iterated
		genname = rule.val
		#rule.val = genname
		# genname -> iterated genname | eps 
		
		looper = Token ("LIST", genname, "0")
		statement = Token ("GENERATOR", iterated, "0")
		empty = Token ("EMPTY", "''", "0")
		
		newrule = [
			[statement, looper],
		#	[statement]
			[empty]
		]
		return genname, newrule, rule

	def checkrightsidegen (self) :
		i, j = self.i, self.j
		if not i < len(self.grammar) :
			return
		check = False
		while self.grammar[i].type in ["RSGEN", "RSIDE"] :
			check = True
			if self.grammar[i].type == "RSGEN" :
				label = self.parsedtokens[j].val
				if label in self.generator_labels[self.current_rule] :
					#operand is Token(val, type, pos)
					operand = self.parsedtokens[j+2]

					#not it yet
					operand.label = label

					#RSGEN catches a NONTERMINAL even if it represents a TOKEN
					#add a data type to recognize them, ex : LABELED_DATA or smth
					#rule.type = "LABELED_DATA"
					unrolledlist = operand
					genname = None
					if operand.val[:5] == "list:" :
						genname, unrolledlist, operand = self.makelistrule(operand)
					elif operand.type == "TERMINAL" :
						operand.val = operand.val[:-1]
					#reactivate if needed for tests 
					#else :
						#operand.type = "NONTERMINAL"
					self.production_rules[self.current_rule][-1].append ( operand )
					self.generator_rules[self.current_rule][self.keyop].append ( operand )
					if genname != None :
						self.production_rules[genname] = unrolledlist
					j += 4
				#print (self.generator_rules)
			else :
				if self.parsedtokens[j].type == "TERMINAL" :
					self.parsedtokens[j].val = self.parsedtokens[j].val[:-1] #eliminate . at terminals
				self.production_rules[self.current_rule][-1].append( self.parsedtokens[j] )
				j += 1
			i += 1
		if check : #add empty rules for generators, makes rule nullable
			self.production_rules[self.current_rule].append([ Token ("EMPTY", "''", "0") ])
		
		self.i, self.j = i, j


