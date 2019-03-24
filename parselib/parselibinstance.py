from parselib.parsers.parsers		 	import CYKParser
from parselib.parsers.grammarparser	 	import GenericGrammarParser, Grammar
from parselib.operations.normoperators	import get2nf
from parselib.datastructure.lexlib		import Tokenizer, Token

from parselib.preprocessor.onepasspreprocessor	import OnePassPreprocessor
from collections import OrderedDict as odict, namedtuple

from parselib.io import Printer, gettextfilecontent

class StructFactory :
	"""Factory generating dataformat from grammar after parsing
	"""
	struct = odict()
	keeper = odict()
	strnodes = list()

	@staticmethod
	def keyInFactory (parent, key) :
		if parent == "AXIOM" : return True
		if not parent in StructFactory.keeper.keys() :
			return False

		return key in StructFactory.keeper[parent]

	@staticmethod
	def keyIsStr (key) :
		return key in StructFactory.strnodes

	@staticmethod
	def strUnfold (node) :
		ss = ""
		for n in node :
			if type(n) == Token :
				ss += n.val + " " #last leaf
			elif type (n) == list :
				ss += StructFactory.strUnfold(n)
			else :
				Printer.showerr("StructFactory.StrUnfold : TypeError")
				exit ()
		return ss.strip() #make it tight 
	@staticmethod
	def readGrammar (grammar) :
		StructFactory.strnodes = grammar.strnodes
		StructFactory.keeper = grammar.keeper

		struct = odict()
		del grammar.keeper["all"]
		for key, val in grammar.keeper.items() :
			structname = key.capitalize()
			components=[v for v in set(val)]
			#Printer.showinfo ("next in factory : ", key, "::", components)
			struct[key] = namedtuple(structname, components)
			struct[key].__new__.__defaults__ = (None,) *len(components)
		StructFactory.struct = struct


	@staticmethod
	def getStruct (structname) :
		#print (structname, StructFactory.struct.keys())
		if structname in StructFactory.struct.keys() :
			return StructFactory.struct[structname]
		return None


class ParselibInstance :

	def __init__ (self) :
		self.grammar   = Grammar()
		self.parser    = None
		self.tokenizer = None

	@staticmethod
	def __getfile (filename) :
		fs = open(filename, "r")
		source = "".join(fs.readlines())
		fs.close()
		return source
	
	def loadGrammar (self, filename, verbose=False) :
		"""builds the instance by loading 
			the grammar from a text file
			
			Parameters
			----------
			filename : str
				string path to file containing text to load
		"""

		gramparser = GenericGrammarParser (OnePassPreprocessor())
		grammar = gramparser.parse (filename, verbose=verbose)

		#normalization
		#grammar = getcnf (grammar)
		grammar = get2nf (grammar)
		self.grammar = grammar

	def processSource (self, filename, verbose=False) :

		StructFactory.readGrammar(self.grammar)
		self.parser = CYKParser (self.grammar)
		source = gettextfilecontent(filename)
		
		tokenizer = Tokenizer(self.grammar.tokens)
		tokenizer.parse (source)

		result = self.parser.membership (tokenizer.tokenized)
		return self.__processResults(result, verbose)

	def __processResults (self, x, verbose=False) :
		""" Unfolds the parse tree and optionnaly prints it
		
			Parameters
			----------
			x : UnitNode, TokenNode, BinNode from parselib.parsetree
				a list of the folded possible parse trees
			verbose : bool
				True (by default) to print results, otherwise False
		"""
		if not x :
			if verbose : 
				Printer.showerr (x) # x should point errors out if parsing failed
			return None
		else :
			if verbose : 
				Printer.showinfo ('number of possible parse trees : ', len(x))
			return self.__parse (
				x[0].unfold(),
				verbose=verbose
			)

	@staticmethod
	def __processnodename (name) :
		if name[-1] == "." :
			return name[:-1]
		return name
	
	def __parse (self, code=[], parent="", verbose=False) :
		"""unfolds parse tree in a factory generated dataformat
		
			Parameters
			----------
			code : parse tree
				result from membership method
			
			parent : str 
				node's parent name
			
			verbose : bool
				True to talk
		"""
		i = 0
		out = odict()
		while i < len(code) :
			element = code[i]
			out_element = None
			
			if element.type == "AXIOM" :
				return self.__parse (element.val, "AXIOM", verbose)
			
			element.type = ParselibInstance.__processnodename(element.type)
			
			#part that handles labels changing (aliases)
			if parent in self.grammar.labels.keys() :
				if element.type in self.grammar.labels[parent].keys() :
					element.type = self.grammar.labels[parent][element.type]


			if StructFactory.keyInFactory(parent, element.type) : #is savable

				if StructFactory.keyIsStr(element.type): # node is str
					out_element = StructFactory.strUnfold (element.val)
				else :
					out_element = self.processnode (element, verbose)
				
				#appending to result
				if element.type in out.keys() :
					out[element.type].append(out_element)
				else :
					out[element.type]=[out_element]
			i += 1
		return out

	def processnode(self, element, verbose):
		# check if object in factory
		tmpClass = StructFactory.getStruct(element.type)
		# object is non terminal
		if tmpClass != None or type(element.val) == list:
			lst = self.__parse(
				code=element.val,
				parent=element.type,
				verbose=verbose
			)  # recurse
			return tmpClass(**lst)

		else:  # terminal node
			return element.val



