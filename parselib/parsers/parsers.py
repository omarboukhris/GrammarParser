from collections import OrderedDict as odict
from parselib.operations.generaloperators import cartesianprod
from parselib.datastructure.parsetree import TokenNode, BinNode, UnitNode

class CYKParser :
	def __init__ (self, grammar) :
		self.production_rules = grammar.production_rules
		self.unitrelation = grammar.unitrelation
		self.err_pos = -1

	def membership (self, word) :
		""" test membership of a word in a grammar
		STABLE AF, DON'T TOUCH
		"""
		n = len(word)
		P = [
			[[] for i in range (n)] for j in range(n)
		]
		
		for i in range (n) :
			P[0][i] = self.getterminal (word[i])
			P[0][i] += self.invUnitRelation (P[0][i])

		for l in range (1, n) :

			for i in range (0, n-l) :

				for k in range (0, l) :
					
					B, A = P[l-k-1][k+i+1], P[k][i]
					AB = cartesianprod (A, B)
					if AB == [] :
						continue

					rulenames = self.getbinproductions (AB)
					P[l][i] += rulenames 
					P[l][i] += self.invUnitRelation (rulenames)
		#self.printmatrix (P)
		
		if P[n-1][0] == [] :
			return False # try returning the broken nodes

		return self.getAxiomNodes (P[n-1][0])

	def getAxiomNodes (self, nodes) :
		axiomnodes = []
		for node in nodes :
			if node.nodetype == 'AXIOM': #self.production_rules["AXIOM"][0][0].val :
				axiomnodes.append (node)
		return axiomnodes

	def invUnitRelation (self, M) :
		""" get inverse unit relation for the parse tree
		"""
		rulenames = []
		for i in range(len(M)) :
			for key, units in self.unitrelation.items() :
				if M[i].nodetype in units :
					node = UnitNode (M[i], key)
					rulenames.append (node)
		M = rulenames
		return rulenames
	
	def getbinproductions (self, AB) :
		""" get a list of binarized production rules
		"""
		keys = list(self.production_rules.keys ()) 
		bins = []
		for line in AB :
			rulenames = self.getrulenames (line)
			for rulename in rulenames :
				#add node for parse tree here
				bins.append (rulename)
		#return list (set(bins))
		return bins
	
	def getrulenames (self, line) :
		""" names suffix is misleading and should be changed
		returns a list of valid nodes corresponding 
		to the rules being inspected
		"""
		if len(line) == 0 :
			return []
		rulenames = []
		for key, rules in self.production_rules.items() :
			for rule in rules :
				if len (rule) == 1 :
					continue

				if rule[0].val == line[0].nodetype and rule[1].val == line[1].nodetype :
					node = BinNode (line[0], line[1], key)
					rulenames.append (node)

		return rulenames

	def getterminal (self, token) :
		""" get terminal nodes for the cyk table + parse tree
		"""
		keys = list(self.production_rules.keys ()) 
		terminals = []
		for v in range(len(keys)) :
			key = keys[v]
			rules = self.production_rules[key]
			for i in range (len(rules)) :
				rule = rules[i]
				if len(rule) == 1 and rule[0].type == "TERMINAL" and rule[0].val == token.type :
					node = TokenNode (key, token.val)
					terminals.append (node)
		return terminals

	def printmatrix (self, p) :
		""" print cyk table for test purposes
		"""	
		ss = ""
		n = len(p)
		for i in range(n) :
			line = p[i]
			for j in range(n-i) :
				el = line[j]
				ss += "{:15}||".format(", ".join([e.__str__() for e in el ]))
			ss += "\n"
		print (ss)
		
