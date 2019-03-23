from parselib.parselibinstance import ParselibInstance

if __name__ == '__main__':
	#=================================== Begin : source code parsing

	parseinst = ParselibInstance ()

	parseinst.loadGrammar("data/grammar.grm")#, verbose=True)
	#parseinst.grammar.save("data/somewhere.pkl")
	#parseinst.grammar.load("data/somewhere.pkl")	
	final = parseinst.processSource("data/test.java")#, verbose=True)

	print (final)
	#==================================== Begin : source code generating
	
	
	# :) :) :) :)
	