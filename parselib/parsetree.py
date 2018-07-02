

class UnitNode :
	def __init__ (self, unit, nodetype) :
		self.unit = unit
		self.nodetype = nodetype
	
	def unfold(self):
		return self.unit.unfold()
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
		self.label = ""

	def unfold(self):
		return self.val #activate for proper parsing
		return "{}({})".format( # activate for debug and naive str parse tree
			self.nodetype,
			self.val
		)
	
	def __str__ (self) :
		return self.nodetype

class LabeledToken :
	def __init__ (self, label, val) :
		self.val = val
		self.label = label

	def unfold(self):

		return {self.label : self.val}
	
	def __str__ (self) :
		return self.unfold()

class LabeledUnit :
	def __init__ (self, label, unit, nodetype) :
		self.unit = unit
		self.label = label
		self.nodetype = nodetype

	def unfold(self):
		#print (self.label[0], self.unit.unfold())
		return {self.label[0] : self.unit.unfold()}

	def __str__ (self) :
		return self.unfold()

class LabeledBin :
	def __init__ (self, label, left, right, nodetype) :
		self.label = label
		self.left = left
		self.right = right
		self.nodetype = nodetype
		
	def unfold (self) :
		pass

class BinNode :
	def __init__ (self, left, right, nodetype) :
		self.left = left
		self.right = right
		self.nodetype = nodetype
		self.label = ""
		
	def unfold(self):
		if type (self.left) != TokenNode :
			if type (self.right) != TokenNode :
				return dict(self.left.unfold(), **self.right.unfold())
			else :
				return self.left.unfold()
		else :
			if type (self.right) != TokenNode :
				return self.right.unfold()
			else :
				return dict()

	def __str__ (self) :
		return self.nodetype


