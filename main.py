from parselib.tests import *

import sys

if __name__ == '__main__':
	
	if len(sys.argv) == 1 :
		test_syntax_pipeline()
	if len(sys.argv) == 2 :
		cmd = sys.argv[1]
		
		if cmd == "--loadgram" :
			test_grammar_loading ()
		
		if cmd == "--all" :
			test_syntax_pipeline()
