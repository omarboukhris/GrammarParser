from collections import OrderedDict as odict
from parselib.generaloperators import cartesianprod
from parselib.parsetree import * #TokenNode, BinNode, UnitNode
import os

"""
generates dot graph from a grammar and stores it in filename.png
this should be updated .. and moved
"""
def dotgraph (gram, filename) :
	ss = "graph {\n"
	for key, rules in gram.production_rules.items() :
		for rule in rules :
			r = [op.val for op in rule]
			r = [i.replace ("-", "") for i in r]
			r = [i.replace (".", "") for i in r]
			r = [i.replace ("\'\'", "eps") for i in r]
			r = [i.replace ("\"\"", "eps") for i in r]
			k = key.replace ("-", "")
			k = k.replace (".", "_tok")
			ss += "\t" + k + " -- " 
			ss += " -- ".join (r)
			ss += " ;\n"
	ss += "}"
	filestream = open (filename + '.dot', 'w') 
	filestream.write(ss)
	filestream.close ()
	cmd = 'dot -Tpng -o ' + filename + '.png ' + filename + '.dot'
	os.system (cmd)
	cmd = 'rm ' + filename + '.dot'
	os.system (cmd)

"""
deprecated parser because is too old, 
but thanks anyway, twas cool to hang out LL
"""
class LLParser :
	def __init__ (self, grammar) :
		self.production_rules = grammar.production_rules
		self.cursor = None
		self.err_pos = None
		self.path = None

	def wordinlanguage (self, word) :
		if len(word) == 0 :
			return True
		self.cursor = 0
		self.path = []
		x = self.checkNode (word, 'AXIOM') 
		self.path.reverse()
		return x and self.cursor == len(word)

	def checkNode (self, word, rulename) :
		for rule in self.production_rules[rulename] :
			if self.dorule (word, rule) :
				ss = rulename + " -> " + "+".join([op.val for op in rule])
				self.path.append (ss)
				return True
		self.err_pos = self.cursor
		return False

	def checkToken (self, word, tokentype) :
		if self.cursor >= len(word) :
			return False
		if word[self.cursor].type == tokentype :
			self.cursor += 1
			return True
		return False

	def dorule (self, word, rule) :
		for operand in rule :
			success = self.dooperand  (word, operand)
			if not success :
				return False 
		return True

	def dooperand (self, word, operand) :
		curs = int(self.cursor)
		if operand.type == "NONTERMINAL" :
			if not self.checkNode (word, operand.val) :
				self.cursor = int(curs)
				return False
			else :
				return True
		else :
			return self.checkToken(word, operand.val) 


class CYKParser :
	def __init__ (self, grammar, unit_lookahead=2) :
		self.production_rules = grammar.production_rules
		self.generator_labels = grammar.generator_labels
		self.unitrelation = grammar.unitrelation
		self.ula = unit_lookahead
		self.err_pos = -1

	"""
	test membership of a word in a grammar
	"""
	def membership (self, word) :
		unit_lookahead = self.ula
		n = len(word)
		P = [
			[[] for i in range (n)] for j in range(n)
		]
		
		for i in range (n) :
			P[0][i] = self.getterminal (word[i])
			P[0][i] = P[0][i] + self.invUnitRelation (P[0][i], unit_lookahead)

		for l in range (1, n) :

			for i in range (0, n-l) :

				for k in range (0, l) :
					
					B, A = P[l-k-1][k+i+1], P[k][i]
					AB = cartesianprod (A, B)
					if AB == [] :
						continue

					rulenames = self.getbinproductions (AB)
					P[l][i] = rulenames 
					P[l][i] = P[l][i] + self.invUnitRelation (rulenames, unit_lookahead)					
		
		#self.printmatrix (P) #activate for debug purposes
		
		if P[n-1][0] == [] :
			return False # try returning the broken nodes

		return self.getAxiomNodes (P[n-1][0])

	def getAxiomNodes (self, nodes) :
		axiomnodes = []
		for node in nodes :
			#print (node.nodetype, self.production_rules["AXIOM"][0][0].val)
			#print (node.unfold())

			if node.nodetype == self.production_rules["AXIOM"][0][0].val :
				axiomnodes.append (node)
		return axiomnodes

	"""
	get inverse unit relation for the parse tree
	"""
	def invUnitRelation (self, M, unit_lookahead) :
		rulenames = []
		for k in range (unit_lookahead) :
			for i in range(len(M)) :
				for key, units in self.unitrelation.items() :
					if M[i].nodetype in units :
						#here will be injected the labeledunitnode class instantiation
						node = None
						if key in self.generator_labels.keys() :
							node = LabeledUnit (self.generator_labels[key], M[i], key)
						else :
							node = UnitNode (M[i], key) 
						rulenames.append (node)
			M = rulenames
		return rulenames
	
	"""
	get a list of binarized production rules
	"""
	def getbinproductions (self, AB) :
		keys = list(self.production_rules.keys ()) 
		bins = []
		for line in AB :
			rulenames = self.getrulenames (line)
			for rulename in rulenames :
				#add node for parse tree here
				bins.append (rulename)
		#return list (set(bins))
		return bins
	
	"""
	names suffix is misleading and should be changed
	returns a list of valid nodes corresponding 
	to the rules being inspected
	"""
	def getrulenames (self, line) :
		if len(line) == 0 :
			return []
		rulenames = []
		for key, rules in self.production_rules.items() :
			for rule in rules :
				if len (rule) == 1 :
					continue

				if rule[0].val == line[0].nodetype and rule[1].val == line[1].nodetype :
					#adapt to labeled node here
					l0, l1 = line[0], line[1]
					
					# also depending on the rule type, use appropriate node class for on the fly gen
					if rule[0].label != "" : 
						l0 = LabeledToken (rule[0].label, line[0].unfold())
					if rule[1].label != "" :
						l1 = LabeledToken (rule[1].label, line[1].unfold())
					

					node = BinNode (l0, l1, key)
					rulenames.append (node)

		return rulenames

	"""
	get terminal nodes for the cyk table + parse tree
	"""
	def getterminal (self, token) :
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

	"""
	print cyk table for test purposes
	"""	
	def printmatrix (self, p) :
		ss = ""
		n = len(p)
		for i in range(n) :
			line = p[i]
			for j in range(n-i) :
				el = line[j]
				ss += "{:15}||".format(", ".join([e.__str__() for e in el ]))
			ss += "\n"
		print (ss)
	