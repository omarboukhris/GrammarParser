from collections import OrderedDict as odict
from parselib.lexlib import Token


class GenericGrammarTokenizer :

	grammartokens = [
		# PREPROCESSOR
		('\%(import|include) \".*\"',	'IMPORT'),
		
		#KEYWORDS
		('(//|\;).*',					'LINECOMMENT'),
		('\'\'|\"\"',					'EMPTY'),
		('AXIOM',						'AXIOM'),
		
		# SPECIAL OPERATORS
		('(\_\_list\_\_|\[\])',			'LIST'),
		('!',							'EXCL'),
		('s\:',							'STR'),
		
		('\(\".*\"\)',					'REGEX'),
		('(\->|\=)',					'EQUAL'),
		#('\,',							'COMMA'),
		('\|',							'OR'),
		('\(',							'LPAR'),
		('\)',							'RPAR'),
		#('\[',							'LCRCH'),
		#('\]',							'RCRCH'),

		#OPERANDS
		('([a-zA-Z_]\w*=)?[a-zA-Z0-9_]\w*\.',		'TERMINAL'),
		('([a-zA-Z_]\w*=)?[a-zA-Z0-9_]\w*',			'NONTERMINAL'),
	]
	
	genericgrammarprodrules = [
		('LINECOMMENT',					          'LINECOMMENT'),
		(r'AXIOM EQUAL (NONTERMINAL|GENERATOR)',		'AXIOM'),
		(r'TERMINAL REGEX',								'TOKEN'),

		(r'NONTERMINAL EQUAL',							'LSIDE'),
		(r'EXCL|STR|LIST|TERMINAL|NONTERMINAL|EMPTY',	'RSIDE'),

		('OR',			'OR'),
		#('COMMA',		'COMMA'),
		('LCRCH',		'LCRCH'),
		('RCRCH',		'RCRCH'),
	]

	@staticmethod
	def _tokenize (tokObj, source, verbose) :
		tokObj.parse (source)
		if verbose : print(tokObj)
		return tokObj


"""
TODO : 
	parse list() operator in a production rule
"""
class SequentialParser :
	def __init__ (self, grammar, parsedtokens) :

		self.axiomflag = True

		self.production_rules = odict()

		self.strnodes = odict()
		self.keeper = odict({'all' : []})
		self.labels = odict()

		self.tokens = list()

		self.grammar = grammar
		self.parsedtokens = parsedtokens


		self.i, self.j, self.current_rule = 0, 0, ""

	def parse (self) :
		while self.stillparsing() :
			self.checkaxiom ()
			self.checkleftside()
			self.checkrightside()
			
			self.checkoperators ()
			self.checkfortoken()
	
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

			if self.parsedtokens[j].type == "STR" :
				#add to strnodes
				if self.current_rule in self.strnodes.keys() :
					self.strnodes[self.current_rule].append(self.parsedtokens[j+1])
				else :
					self.strnodes[self.current_rule] = [self.parsedtokens[j+1]]

				#add to keeper to tell the parser to save this node's content
				if self.current_rule in self.keeper.keys() :
					self.keeper[self.current_rule].append(self.parsedtokens[j+1])
				else :
					self.keeper[self.current_rule] = [self.parsedtokens[j+1]]

				if not self.parsedtokens[j+1].val in self.keeper["all"] :
					if self.parsedtokens[j+1].type == "TERMINAL" :
						self.keeper["all"].append(self.parsedtokens[j+1].val[:-1])
					else :
						self.keeper["all"].append(self.parsedtokens[j+1].val)
				j+=1
				i+=1
				continue

			if self.parsedtokens[j].type == "LIST" :
				thisnode = Token ("NONTERMINAL", self.current_rule, 0)
				eps = Token("EMPTY", '""', 0)
				self.production_rules[self.current_rule][-1] = [thisnode, thisnode]
				self.production_rules[self.current_rule].append([eps])
				j+=1
				i+=1
				continue

			if self.parsedtokens[j].type == "EXCL" :

				#add to keeper to tell the parser to save this node's content
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
			if i <= len(self.grammar) :
				break
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






