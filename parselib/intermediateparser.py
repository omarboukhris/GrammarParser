from parselib.lexlib import Tokenizer

class IntermediateParser :

	def __init__ (self) :
		"""
		"""
		self.parsedsourcetokens = [
			("[a-zA-Z0-9_]\w*\.",    "LABEL"),
			("\(.*\)",               "TERM"),
			("[a-zA-Z0-9_]\w*",      "NONTERM"),
			("\= \[",                "BEGIN"),
			("\]",                   "END"),
		]
	
	def parse_ (self, strcode="", verbose=False) :
		"""parse code once it passed syntaxic analysis phase
		
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

	def parse (self, strcode="", verbose=False) :
		parsed = self.parse_ (strcode, verbose)

		for element in parsed :
			
			if element.type == "LABEL" : #this is a labeled terminal
				#deal with terminal
				pass
			elif element.type == "BEGIN" :
				#read until element.type == "END"
				#this is the parsed right side of a production rule
				pass
			elif element.type == "NONTERM" :
				#create non termina node
				pass
			else :
				#shit hit the fan
				pass


