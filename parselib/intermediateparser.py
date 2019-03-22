from parselib.lexlib import Tokenizer, Token
from collections import OrderedDict as odict, namedtuple



class StructFactory :
	struct = odict()
	keeper_all = odict()
	keeper = odict()

	@staticmethod
	def readGrammar (grammar) :
		struct = odict()
		for key, val in grammar.keeper.items() :
			structname = key.capitalize()
			components=", ".join(
				[
					str(
						v.val if type(v) != str else v
					) for v in set(val)
				]
			)
			struct[key] = namedtuple(structname, components)
		StructFactory.struct = struct
		StructFactory.keeper_all = grammar.keeper["all"]
		del grammar.keeper["all"]
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


class IntermediateParser :

	def __init__ (self) :
		self.parsedsourcetokens = [
			("[a-zA-Z0-9_]\w*\.",    "LABEL"),
			("\(.*\)",               "TERM"),
			("[a-zA-Z0-9_]\w*",      "NONTERM"),
			("\= \[",                "BEGIN"),
			("\]",                   "END"),
		]
	
	def tokenize (self, strcode="", verbose=False) :
		"""tokenize code once it passed syntaxic analysis phase
		
		strcode : str
			source code in intermediate form
		
		verbose : bool
			True to make it talk. False by default
		"""
		
		tokenizer = Tokenizer (self.parsedsourcetokens)
		tokenizer.parse (strcode)
		
		if verbose : 
			print(tokenizer)
		return tokenizer.tokenized

	@staticmethod
	def __processnodename (name) :
		if name[-1] == "." :
			return name[:-1]
		return name

	def parse (self, strcode=[], verbose=False) :
		i = 0
		out = []
		while i < len(strcode) :
			element = strcode[i]
			out_element = None
			
			if element.type == "AXIOM" :
				return self.parse (element.val, verbose)
			
			#works nice (almost)
			#needs to aggregate missing data in branching nodes
			
			element.type = IntermediateParser.__processnodename(element.type)
			if StructFactory.keyInFactory(element.type) : #is savable
				#print ("key in factory : ", element.type, StructFactory.keeper_all)
				tmpClass = StructFactory.getStruct(element.type)

				if tmpClass != None : #found in factory
					lst = self.parse(element.val, verbose) #recurse
					#print ("element val is list (factory) : ", lst)
					out_element = tmpClass(*lst)

				else :
					if type(element.val) == list :
						lst = self.parse(element.val, verbose) #recurse
						#print ("element val is list : ", lst)
						out_element = tmpClass(*lst)
					else :
						out_element = element.val
				out.append(out_element)
			i += 1
		return out







