from parselib.datastructure.lexlib 		import Tokenizer
from parselib.operations.generaloperators 	import transformtosource, eliminatedoubles
from parselib.operations.naiveparsers 		import SequentialParser, GenericGrammarTokenizer

from collections import OrderedDict as odict
import pickle, random, json, os

import parselib.io as io

class Grammar :
	def __init__ (self) :
		self.production_rules = odict()
		self.labels = odict()
		self.keeper = odict()
		self.unitrelation = odict()
		self.strnodes = list()
		self.tokens = list()

	def merge (self, grammar) :
		#unitrelation in computed later
		self.tokens += grammar.tokens
		#production_rules merge
		for key, rules in grammar.production_rules.items() :
			if key in self.production_rules.keys() :
				self.production_rules[key] += rules
			else :
				self.production_rules[key] = rules
			
		#labels merge
		for key, val in grammar.labels.items() :
			if key in self.labels.keys() :
				self.labels[key].update(val)
			else :
				self.labels[key] = val

		#keeper merge
		for key, val in grammar.keeper.items() :
			if key in self.keeper.keys() :
				self.keeper[key] += val
			else :
				self.keeper[key] = val
			
			self.keeper["all"] = list(set(self.keeper["all"]+val))
		self.strnodes += grammar.strnodes



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
		self.strnodes = ngp.strnodes

		self.keeper = odict() #ngp.keeper
		for k, val in ngp.keeper.items() :
			self.keeper[k] = [v.val if type(v) != str else v for v in val]
			self.keeper[k] = list(set(self.keeper[k]))


		self = eliminatedoubles (self)
		#gramtest = checkproductionrules(self.production_rules) #is fuckedup
		#return gramtest
		return []

	def saveGraph (self, filename) :
		"""generates dot graph from a grammar and stores it in filename.png
		this should be updated .. and moved
		"""
		ss = "digraph {\n"
		for key, rules in self.production_rules.items() :
			for rule in rules :
				r = [op.val for op in rule]
				r = [i.replace ("-", "") for i in r]
				r = [i.replace (".", "") for i in r]
				r = [i.replace ("\'\'", "eps") for i in r]
				r = [i.replace ("\"\"", "eps") for i in r]
				r = [i.replace ("/", "_") for i in r]
				k = key.replace ("-", "")
				k = k.replace ("/", "_")
				k = k.replace (".", "_tok")
				ss += "\t" + k + " -> " 
				ss += " -> ".join (r)
				ss += " ;\n"
		ss += "}"
		filestream = open (filename + '.dot', 'w') 
		filestream.write(ss)
		filestream.close ()
		cmd = 'dot -Tpng -o ' + filename + '.png ' + filename + '.dot'
		os.system (cmd)
		cmd = 'rm ' + filename + '.dot'
		os.system (cmd)


	def save (self, filename) :
		"""save parsed grammar in pickle file"""
		serialFile = open (filename, "wb")
		pickle.dump (self.production_rules, serialFile)
		pickle.dump (self.unitrelation, serialFile)
		pickle.dump (self.labels, serialFile)
		pickle.dump (self.keeper, serialFile)
		pickle.dump (self.strnodes, serialFile)
		pickle.dump (self.tokens, serialFile)
		serialFile.close()
	def load (self, filename) :
		"""load grammar from pickle file"""
		serialFile = open (filename, "rb")
		self.production_rules = pickle.load (serialFile)
		self.unitrelation = pickle.load (serialFile)
		self.labels = pickle.load (serialFile)
		self.keeper = pickle.load (serialFile)
		self.strnodes = pickle.load(serialFile)
		self.tokens = pickle.load (serialFile)
		serialFile.close()

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
					key, ", \n\t\t".join(val)
				) for key, val in self.keeper.items()
			])
		)
		text_rule += "STRNODE = [\n{}\n]\n\n".format(
			"".join(self.strnodes)
		)
		for regex, label in self.tokens :
			text_rule += "TOKEN " + label + " = regex('" + regex + "')\n"

		return text_rule
		

class GenericGrammarParser :
	
	def __init__ (self, preproc) :
		
		#preprocessor class
		self.preproc = preproc
		

	def parse (self, filename, verbose=False) :
		"""lex a grammar from textual form to tokenized
		
			Parameters
			----------
			txt_grammar : str
				raw grammar source code
			
			verbose : bool
				True to make it talk. False by default
		"""
		out_grammar = Grammar()
		self.preproc.addToQueue (filename)

		while not self.preproc.queueIsEmpty() :

			#tokenize grammar source
			filename = self.preproc.queue[0]
			source = io.gettextfilecontent (filename)
			lang = GenericGrammarTokenizer._tokenize (
				Tokenizer (GenericGrammarTokenizer.grammartokens), 
				source,
				verbose
			)
			
			#preprocessor here (one pass preprocessor)
			lang.tokenized = self.preproc.preprocess (filename, lang.tokenized)

			#text tokens are needed for next step
			txtok = transformtosource (lang.tokenized)
			#tokenize in abstract grammar tokens
			gram = GenericGrammarTokenizer._tokenize (
				Tokenizer (GenericGrammarTokenizer.genericgrammarprodrules),
				txtok,
				verbose
			)

			##make production rules
			grammar = Grammar ()
			result = grammar.makegrammar (
				gram.tokenized,
				lang.tokenized,
			)
			if (result == []) :
				if verbose : print (grammar)
				out_grammar.merge (grammar)
			else :
				io.Printer.showerr (result)
				return Grammar()

		return out_grammar

