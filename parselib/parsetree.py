

class UnitNode :
	def __init__ (self, unit, nodetype) :
		self.unit = unit
		self.nodetype = nodetype

	def iscompacted (self) :
		return self.nodetype.find("/") != -1

	def unfold(self, parent=None):
		if self.iscompacted() or parent == self.nodetype :
			return self.unit.unfold(self.nodetype)
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

		return "{}({})".format(
			self.nodetype,
			self.val
		)
	
	def __str__ (self) :
		return self.nodetype

class BinNode :
	def __init__ (self, left, right, nodetype) :
		self.left = left
		self.right = right
		self.nodetype = nodetype
	
	def iscompacted (self) :
		return self.nodetype.find("/") != -1
	
	def unfold(self, parent=None):
		if self.iscompacted() or parent == self.nodetype :
			return "{} + {}".format(
			self.left.unfold(self.nodetype),
			self.right.unfold(self.nodetype),
		)
			
		return "{} = [ {} + {} ]".format(
			self.nodetype,
			self.left.unfold(self.nodetype),
			self.right.unfold(self.nodetype),
		)
	
	def __str__ (self) :
		return self.unfold() #self.nodetype


