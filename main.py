from parselib.parselibinstance import ParselibInstance

if __name__ == '__main__':

	#=================================== Begin : source code parsing
	#list operator not implemented yet
	parseinst = ParselibInstance ()

	parseinst.loadGrammar("data/grammar.grm", verbose=True)
	#parseinst.grammar.save("data/somewhere.pkl")
	#parseinst.grammar.load("data/somewhere.pkl")	
	final = parseinst.processSource("data/test.java")#, verbose=True)

	print (final) #datastructure with parsed savable data


	#==================================== Begin : source code generating
	
	
	# :) :) :) :)
	