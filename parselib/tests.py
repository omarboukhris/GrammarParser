from parselib import *

def processverbose (verbose) :
	try :
		return int(verbose) != 0
	except :
		print ("ValueError : verbose set on True")
		return True


def pipeline (gramfile, filename, verbose) :
	verbose = processverbose (verbose)
	
	parseinst = ParselibInstance ()

	parseinst.loadGrammar(gramfile, verbose=verbose)
	
	final = parseinst.processSource(filename, verbose)

	print (final) #datastructure with parsed savable data


def load_grammar (filename, verbose) :
	parseinst = ParselibInstance ()

	parseinst.loadGrammar(filename, verbose)

def parse_save (filename, verbose=False) :
	verbose = processverbose (verbose) 
	
	parseinst = ParselibInstance ()

	#test grammar loading
	parseinst.loadGrammar(filename, verbose=verbose)
	
	#graph exportation using dot
	parseinst.grammar.saveGraph ("data/out")

	#serialization
	parseinst.grammar.save("data/somewhere.pkl")

def test_load_gram_from_file (filename) :	
	parseinst = ParselibInstance ()
	parseinst.grammar.load(filename)

	final = parseinst.processSource("data/test.java", verbose=True)

	print (final) #datastructure with parsed savable data
