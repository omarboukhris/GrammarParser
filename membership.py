from parselib import ParselibInstance
from parselib.utils.io	import ArgvLex, Printer

import sys

def processverbose (verbose) :
	try :
		return int(verbose) != 0
	except :
		print ("ValueError : verbose set on True")
		return True

def membership_processor (gramfile, filename, verbose) :
	verbose = processverbose (verbose)
	
	parseinst = ParselibInstance ()

	parseinst.loadGrammar(gramfile, verbose=verbose)
	
	final = parseinst.processSource(filename, verbose)

	if verbose :
		Printer.showinfo (final)

def showhelp () :
	print ("""
membership --gsrc=grammar/source.grm --src=source/code [-v]
\tgsrc : grammar source file
\tsrc  : source code to check membership
\t-v   : verbose (optional)
	""")
	
if __name__ == '__main__':
	#command line argument parser
	argshlex = ArgvLex (sys.argv[1:])

	if argshlex.get("-h") or argshlex.get("--help") :
		showhelp()
	if argshlex.get("--gsrc") and argshlex.get("--src") :
		membership_processor (
			argshlex.get("--gsrc"),
			argshlex.get("--src"),
			argshlex.get("-v")
		)



