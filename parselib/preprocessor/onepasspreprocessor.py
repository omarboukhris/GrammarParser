
class DummyPreprocessor :
	
	def __init__ (self) :
		self.parselibinstance = None
		self.queue = []
	
	def preprocess (self, tokenlist) :
		out_tokenlist = []
		
		#return out_tokenlist
		return tokenlist

class OnePassPreprocessor :
	verbose=True
	
	def __init__ (self) :
		self.pwd = ""
		self.queue = []
		self.processed = [] #to avoid meaningless import looping
	
	def addToQueue (self, filename) :
		self.queue.append(filename)
	def removeFromQueue (self, filename) :
		# remove filename from queue
		while filename in self.queue :
			self.queue.remove (filename)
	def queueIsEmpty (self) :
		return self.queue == []
			
	def isProcessed (self, filename) :
		return filename in self.processed
	def addToProcessed (self, filename) :
		self.processed.append (filename)
	
	def preprocess (self, filename, tokenlist) :
		self.removeFromQueue (filename)
		
		if self.isProcessed(filename) :
			return []

		#current grammar directory 
		self.pwd = "/".join(filename.split("/")[:-1])
		
		out_tokenlist = self._processimports (tokenlist)
		self.addToProcessed (filename)
		
		return out_tokenlist

	def _processimports (self, tokenlist) :
		outtok = []
		for token in tokenlist :
			
			if token.type == "IMPORT" :
				filename = self.pwd + "/" + token.val[9:-1]
				self.addToQueue (filename)
			else :
				outtok.append (token)
		return outtok
		
		
		

