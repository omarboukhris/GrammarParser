

class UnitNode :
	def __init__ (self, unit, nodetype) :
		self.unit = unit
		self.nodetype = nodetype

	def iscompacted (self) :
		return self.nodetype.find("/") != -1

	def unfold(self, parent=None):
		if self.iscompacted() or parent == self.nodetype :
			return self.unit.unfold(self.nodetype)
		else :
			return {
				self.nodetype : self.unit.unfold()
			}

		return "( {} -> {} )".format(
			self.nodetype,
			self.unit.unfold(self.nodetype),
		)

	def __str__ (self) :
		return self.nodetype

class TokenNode :
	def __init__ (self, nodetype, val) :
		self.nodetype = nodetype
		self.val = val

	def unfold(self, parent=None):
		return {self.nodetype : self.val}
		#return "{}({})".format(
			#self.nodetype,
			#self.val
		#)
	
	def __str__ (self) :
		return self.nodetype

class BinNode :
	def __init__ (self, left, right, nodetype) :
		self.left = left
		self.right = right
		self.nodetype = nodetype

	#forcefully binarized rule
	def iscompacted (self) :
		return self.nodetype.find("/") != -1
	def islistnode (self) :
		return self.right.nodetype == self.left.nodetype
	
	def makelist(self) :
		r = self.right.unfold(self.nodetype)
		l = self.left.unfold(self.nodetype)
		
		
		#print ('>>>>>>>>\n', r,'\n', l,'\n')

		result = {}
		if r.keys() == l.keys() :
			#print ( '>>>>>keys\n', r.keys(), l.keys(), '>>>>>keys\n')
			for k, v in l.items() :
				if type(r[k]) != list :
					r[k] = [r[k]]
				if type(l[k]) != list :
					l[k] = [l[k]]
				result[k] = r[k] + l[k]
			#return result
		else :
			if self.nodetype in r.keys() :
				r = r[self.nodetype]
			
			if self.nodetype in l.keys() :
				l = l[self.nodetype]

			r.update(l)
			result = {self.nodetype:r}
			
		#print ('<<<<<<<<<<\n',result, '\n')
		
		return result


	def unfold(self, parent=None):
		if self.islistnode() : #we have a list
			return self.makelist ()
		
		if self.iscompacted() or parent == self.nodetype : 
			return self.mergedicts(
			#return "{} + {}".format( # make it merge two dicts
				self.left.unfold(self.nodetype),
				self.right.unfold(self.nodetype),
			)
		else :
			return self.makedict (
			#return "{} = [ {} + {} ]".format(
				self.nodetype,
				self.left.unfold(self.nodetype),
				self.right.unfold(self.nodetype),
			)
	
	def mergedicts (self, dl, dr):
		dl.update(dr)
		return dl
		
	def makedict (self, node, d1, d2) :
		return {node : self.mergedicts (d1, d2)}
	
	def __str__ (self) :
		return self.unfold().__str__() #self.nodetype
