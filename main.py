from parselib.parselibinstance import ParselibInstance

import sys, json

if __name__ == '__main__':
	
	parseinst = ParselibInstance ()

	parseinst.loadGrammar("data/grammar.grm")

	parseinst.grammar.save("data/somewhere.pkl")

	parseinst.grammar.load("data/somewhere.pkl")
	final = parseinst.processSource("data/test.java")

	print (final)
