from collections import OrderedDict as odict
import os

class Node :
	def __init__ (self, left, right, nodetype, val) :
		self.left = left
		self.right = right
		self.nodetype = nodetype
		self.val = val
	
	def unfold(self):
		if self.left == None and self.right == None:
			return "{} = '{}'\n".format(self.nodetype, self.val)

		return "{} = [ \n{}{}]\n".format(
			self.nodetype,
			self.left.unfold(),
			self.right.unfold(),
		)
	
	def __str__ (self) :
		return self.nodetype

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
	def __init__ (self, grammar) :
		self.production_rules = grammar.production_rules
		self.err_pos = -1
		
	def wordinlanguage (self, word) :
		n = len(word)
		P = [
			[[] for i in range (n)] for j in range(n)
		]
		
		for i in range (n) :
			P[0][i] = self.getterminal (word[i])
		for i in range (n-1) :
			AB = self.cartesianprod (P[0][i], P[0][i+1])
			if AB == [] :
				continue
			rulenames = self.getbinproductions (AB)
			if rulenames == [] :
				continue
			P[1][i] += rulenames 

		for l in range (2, n) :

			for i in range (0, n-l) :
				
				for k in range (0, l) :
					
					B, A = P[l-k-1][k+i+1], P[k][i]
					AB = self.cartesianprod (A, B)
					if AB == [] :
						continue

					rulenames = self.getbinproductions (AB)
					if rulenames == [] :
						continue
					P[l][i] = rulenames 
			self.printmatrix (P)

		if P[n-1][0] == [] :
			return False # try retruning the broken nodes
		#print (P[n-1][0][0].nodetype, self.production_rules["AXIOM"][0][0].val)
		#return P[n-1][0][0].nodetype == self.production_rules["AXIOM"][0][0].val
		return P[n-1][0][0]
	
	def cartesianprod (self, A, B) :
		AB = []
		if A == [] :
			return []
		if B ==  [] :
			return []
		for a in A :
			for b in B :
				AB.append ([a, b])
		return AB
	
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
	
	def getrulenames (self, line) :
		rulenames = []
		if len(line) == 0 :
			return []
		for key, rules in self.production_rules.items() :
			for rule in rules :
				if len (rule) == 1 :
					#unit handling goes here (maybe ?)
					#not sure yet
					#do a case study or two to get an idea about methodology
					continue
				#wtf is up with eps rules
				
				#if rule[0].val == line[0] and rule[1].val == line[1] :
				#print( rule[0].val, line[0].nodetype, rule[1].val, line[1].val)

				if rule[0].val == line[0].nodetype and rule[1].val == line[1].nodetype :
					node = Node (line[0], line[1], key, None)
					rulenames.append (node)
					#rulenames.append (key)
		#return list (set(rulenames))
		return rulenames

	def getterminal (self, token) :
		keys = list(self.production_rules.keys ()) 
		unit_index = []
		for v in range(len(keys)) :
			key = keys[v]
			rules = self.production_rules[key]
			for i in range (len(rules)) :
				rule = rules[i]
				if len(rule) == 1 and rule[0].type == "TERMINAL" and rule[0].val == token.type :
					node = Node (None, None, key, token.val)
					unit_index.append (node)
					#unit_index.append (key)
		#return list(set(unit_index))
		return unit_index
	
	def printmatrix (self, p) :
		ss = ""
		n = len(p)
		for i in range(n) :
			line = p[i]
			for j in range(n-i) :
				el = line[j]
				ss += "{:15}".format(", ".join([e.__str__() for e in el ]))
			ss += "\n"
		print (ss)
	
	def count_nonterminals (self) :
		return len(self.production_rules.keys())
		