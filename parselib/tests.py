from parselib.parselibinstance import *

def test_syntax_pipeline () :
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar("data/grammar.grm", verbose=True)

	#graph exportation using dot
	parseinst.grammar.saveGraph ("data/out")

	#serialization
	#parseinst.grammar.save("data/somewhere.pkl")
	#parseinst.grammar.load("data/somewhere.pkl")

	final = parseinst.processSource("data/test.java", verbose=True)

	print (final) #datastructure with parsed savable data


def test_grammar_loading () :
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar("data/grammar.grm", verbose=True)

def test_load_gram_from_file (filename) :	
	parseinst = ParselibInstance ()
	parseinst.grammar.load(filename)

	final = parseinst.processSource("data/test.java", verbose=True)

	print (final) #datastructure with parsed savable data




