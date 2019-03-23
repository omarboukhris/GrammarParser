from parselib.grammarparser			import *
from parselib.parsers				import *
from parselib.generaloperators		import *
from parselib.normoperators			import *
from parselib.lexlib				import Tokenizer, Token
from parselib.io					import Printer

from collections import OrderedDict as odict, namedtuple



class StructFactory :
	struct = odict()
	keeper_all = odict()
	keeper = odict()

	@staticmethod
	def readGrammar (grammar) :
		struct = odict()
		StructFactory.keeper_all = grammar.keeper["all"]
		del grammar.keeper["all"]
		for key, val in grammar.keeper.items() :
			structname = key.capitalize()
			components=[str(
					v.val if type(v) != str else v
				) for v in set(val)
			]
			#Printer.showinfo ("next in factory : ", key, "::", components)
			struct[key] = namedtuple(structname, components, defaults=(None,)*len(components))
		StructFactory.struct = struct
		StructFactory.keeper = grammar.keeper

	@staticmethod
	def keyInFactory (key) :
		return key in StructFactory.keeper_all

	@staticmethod
	def getStruct (structname) :
		#print (structname, StructFactory.struct.keys())
		if structname in StructFactory.struct.keys() :
			return StructFactory.struct[structname]
		return None


class ParselibInstance :

	def __init__ (self) :
		self.grammar   = None
		self.parser    = None
		self.tokenizer = None
		
		
	def loadGrammar (self, filename, verbose=False) :
		"""builds the instance by loading 
		the grammar from a text file
		
		Parameters
		----------
		filename : str
			string path to file containing text to load
		"""
		fs = open(filename, "r")
		source = "".join(fs.readlines())
		fs.close()

		gramparser = GenericGrammarParser ()
		grammar = gramparser.parse (source,	verbose=verbose)

		#normalization
		#grammar = getcnf (grammar)
		grammar = get2nf (grammar)
		self.grammar = grammar
		self.parser = CYKParser (self.grammar)
		StructFactory.readGrammar(self.grammar)

	def processSource (self, filename, verbose=False) :
		fs = open(filename, "r")
		source = "".join(fs.readlines())
		fs.close()
		
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
			return self.__parse (x[0].unfold(),verbose=verbose)

	@staticmethod
	def __processnodename (name) :
		if name[-1] == "." :
			return name[:-1]
		return name
	
	def __parse (self, strcode=[], verbose=False) :
		i = 0
		out = odict()
		while i < len(strcode) :
			element = strcode[i]
			out_element = None
			
			if element.type == "AXIOM" :
				return self.__parse (element.val, verbose)
			
			#works nice (almost)
			#needs to aggregate missing data in branching nodes -ex classbody
			
			element.type = ParselibInstance.__processnodename(element.type)
			if StructFactory.keyInFactory(element.type) : #is savable
				#print ("key in factory : ", element.type, StructFactory.keeper_all)
				tmpClass = StructFactory.getStruct(element.type)
				
				if tmpClass != None or type(element.val) == list :
					lst = self.__parse(element.val, verbose) #recurse
					#Printer.showinfo ("element val is list : ", element.type, "::",  len(lst), "::", lst, "::", tmpClass._fields)
					#lst = IntermediateParser.__mergenodes (lst, tmpClass)
					out_element = tmpClass(**lst)
				else :
					#print ("element val ::::: ", element.val) 
					out_element = element.val
				if element.type in out.keys() :
					out[element.type].append(out_element)
				else :
					out[element.type]=[out_element]
			i += 1
		return out






