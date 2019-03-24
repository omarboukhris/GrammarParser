from parselib.parselibinstance import *

class ArgvLex :
	
	def __init__ (self, argv) :
		self.parsedargv = {}
		for arg in argv :
			s = arg.split("=")
			if len(s) == 1 :
				self.parsedargv[s[0]] = True
			elif len(s) == 2 :
				self.parsedargv[s[0]] = s[1]
			#else :
				#pass
	def get (self, key) :
		if key in self.parsedargv.keys() :
			return self.parsedargv[key]
		return False
		

def test_syntax_pipeline () :
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar("data/grammar.grm", verbose=True)

	#graph exportation using dot
	parseinst.grammar.saveGraph ("data/out")

	#serialization
	parseinst.grammar.save("data/somewhere.pkl")
	parseinst.grammar.load("data/somewhere.pkl")	

	final = parseinst.processSource("data/test.java", verbose=True)

	print (final) #datastructure with parsed savable data


def test_grammar_loading () :
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar("data/grammar.grm", verbose=True)

	



