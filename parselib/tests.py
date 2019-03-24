from parselib.parselibinstance import *

def processverbose (verbose) :
	try :
		return int(verbose) != 0
	except :
		print ("ValueError : verbose set on True")
		return True


def test_syntax_pipeline (verbose=False) :
	verbose = processverbose (verbose)
	
	parseinst = ParselibInstance ()

	parseinst.loadGrammar("data/grammar.grm", verbose=verbose)
	
	final = parseinst.processSource("data/test.java", verbose=verbose)

	print (final) #datastructure with parsed savable data


def test_grammar_loading () :
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar("data/grammar.grm", verbose=True)

def test_parse_save (verbose=False) :
	verbose = processverbose (verbose) 
	
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar("data/grammar.grm", verbose=verbose)
	
	#graph exportation using dot
	parseinst.grammar.saveGraph ("data/out")

	#serialization
	parseinst.grammar.save("data/somewhere.pkl")

def test_load_gram_from_file (filename) :	
	parseinst = ParselibInstance ()
	parseinst.grammar.load(filename)

	final = parseinst.processSource("data/test.java", verbose=True)

	print (final) #datastructure with parsed savable data
