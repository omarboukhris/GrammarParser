from parselib.tests import *
from parselib.io	import ArgvLex

import sys

if __name__ == '__main__':
	#command line argument parser
	argshlex = ArgvLex (sys.argv[1:])

	if argshlex.get("--loadgram") :
		test_grammar_loading ()
	
	elif argshlex.get("--parsesave") :
		test_parse_save (argshlex.get("--parsesave"))
	
	elif argshlex.get("--all") :
		test_syntax_pipeline(argshlex.get("--all"))

	elif argshlex.get("--loadsaved") :
		test_load_gram_from_file (argshlex.get("--loadsaved"))

