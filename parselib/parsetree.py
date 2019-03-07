

class UnitNode :
	def __init__ (self, unit, nodetype) :
		self.unit = unit
		self.nodetype = nodetype
	
	def unfold(self):

		return "( {} -> {} )".format(
			self.nodetype,
			self.unit.unfold(),
		)

	def __str__ (self) :
		return self.nodetype

class TokenNode :
	def __init__ (self, nodetype, val) :
		self.nodetype = nodetype
		self.val = val

	def unfold(self):

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
	
	def unfold(self):
		if self.iscompacted() :
			return "{} + {}".format(
			self.left.unfold(),
			self.right.unfold(),
		)
			
		return "{} = [ {} + {} ]".format(
			self.nodetype,
			self.left.unfold(),
			self.right.unfold(),
		)
	
	def __str__ (self) :
		return self.nodetype


