from parselib.tests import *
from parselib.utils.io	import ArgvLex

import sys

if __name__ == '__main__':
	#command line argument parser
	argshlex = ArgvLex (sys.argv[1:])

	if argshlex.get("--loadgram") :
		load_grammar (
			argshlex.get("--loadgram"), 
			argshlex.get("-v")
		)
	
	elif argshlex.get("--parsesave") :
		parse_save (
			argshlex.get("--parsesave"), 
			argshlex.get("-v")
		)
	
	elif argshlex.get("--all") :
		pipeline(
			argshlex.get("--gram"),
			argshlex.get("--source"),
			argshlex.get("-v")
		)
	else :
		print ("""
options :
	--loadgram=file  : load grammar
	--parsesave=file : parse grammar file and serialize
	--all            : load, store, parse ...
	--gram           : grammar file
	--source         : source file
	-v               : verbose
		""")
