from parselib.naiveparsers 	import GenericGrammarTokenizer
from parselib.lexlib		import Tokenizer
from parselib.io			import gettextfilecontent

class DummyPreprocessor :
	
	def __init__ (self) :
		self.parselibinstance = None
		self.queue = []
	
	def preprocess (self, tokenlist) :
		out_tokenlist = []
		
		#return out_tokenlist
		return tokenlist

class Preprocessor :
	verbose=True
	
	def __init__ (self) :
		self.queue = []
		self.processed = [] #to avoid meaningless import looping
	
	def preprocess (self, filename, tokenlist) :
		# remove filename from queue
		while filename in self.queue :
			self.queue.remove (filename)

		# if processed then exit function
		if filename in self.processed :
			return []

		out_tokenlist = []
		
		#process imports then queue
		# _ += _ is vector concat 
		out_tokenlist += self._processimports (tokenlist) #1st pass
		self.processed.append (filename)
		
		#out_tokenlist += self.processQueue ()
		
		print ([str(i) for i in out_tokenlist])
		
		return out_tokenlist

	def processQueue (self) :
		
		out_tokenlist = []
		
		for langfile in self.queue :
			source = gettextfilecontent (langfile)
			tokenlist = GenericGrammarTokenizer._tokenize (
				Tokenizer (GenericGrammarTokenizer.grammartokens), 
				source,
				verbose=Preprocessor.verbose
			)
			out_tokenlist += tokenlist.tokenized
			
			#vector concatenation
			#out_tokenlist += self._processimports (tokenlist.tokenized) #all the other passes
			#self.processed.append (langfile)
			#out_tokenlist += self.processQueue ()
			
			
		self.queue = []

		return out_tokenlist

	def _processimports (self, tokenlist) :
		outtok = []
		for token in tokenlist :
			
			if token.type == "IMPORT" :
				filename = token.val[9:-1]
				self.queue.append (filename)
			else :
				outtok.append (token)
		return outtok
		
		
		

