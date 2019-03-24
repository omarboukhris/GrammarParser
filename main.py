from parselib.tests import *

import sys

if __name__ == '__main__':

	#command line argument parser
	argshlex = ArgvLex (sys.argv[1:])

	if argshlex.get("--loadgram") :
		test_grammar_loading ()
	
	if argshlex.get("--all") :
		test_syntax_pipeline()
