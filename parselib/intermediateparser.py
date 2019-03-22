
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
	
	def parsecode (self, strcode="", verbose=False) :
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



