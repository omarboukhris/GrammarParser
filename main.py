from parselib.parselibinstance import ParselibInstance

if __name__ == '__main__':
	#=================================== Begin : source code parsing
	# TODO : handle labels changing
	
	parseinst = ParselibInstance ()

	parseinst.loadGrammar("data/grammar.grm")

	#parseinst.grammar.save("data/somewhere.pkl")
	#parseinst.grammar.load("data/somewhere.pkl")
	
	final = parseinst.processSource("data/test.java")

	print (final)
	#==================================== Begin : source code generating
	
	
	# :) :) :) :)
	