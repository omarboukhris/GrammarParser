from parselib.lexlib import Tokenizer, Token
from parselib.io import Printer
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
	
	@staticmethod
	def __mergenodes (nodes, _Class) :
		out = odict()
		for elm in _Class._fields :
			out[elm] = []
			for node in nodes :
				name = node.lower() if type(node) == str else node.type.lower() #== nom de la regle
				if name == elm :
					out[elm].append(node)
			if len(out[elm]) == 1 :
				print(out[elm])
				out[elm] = out[elm][0]
		Printer.showinfo(out, "::", nodes)
		return out

	def parse (self, strcode=[], verbose=False) :
		i = 0
		out = odict()
		while i < len(strcode) :
			element = strcode[i]
			out_element = None
			
			if element.type == "AXIOM" :
				return self.parse (element.val, verbose)
			
			#works nice (almost)
			#needs to aggregate missing data in branching nodes -ex classbody
			
			element.type = IntermediateParser.__processnodename(element.type)
			if StructFactory.keyInFactory(element.type) : #is savable
				#print ("key in factory : ", element.type, StructFactory.keeper_all)
				tmpClass = StructFactory.getStruct(element.type)
				
				if tmpClass != None or type(element.val) == list :
					lst = self.parse(element.val, verbose) #recurse
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







