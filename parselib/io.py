

class ArgvLex :
	
	def __init__ (self, argv) :
		self.parsedargv = {}
		for arg in argv :
			s = arg.split("=")
			if len(s) == 1 :
				self.parsedargv[s[0]] = True
			elif len(s) == 2 :
				self.parsedargv[s[0]] = s[1]
			#else :
				#pass
	def get (self, key) :
		if key in self.parsedargv.keys() :
			return self.parsedargv[key]
		return False
		
class Printer :
	
	@staticmethod
	def showinfo (*ss) :
		print ("[info] ", *ss)
	
	@staticmethod
	def showerr (*ss) :
		print ("[error] ", *ss)

def gettextfilecontent (filename):
	try :
		fs = open(filename, "r")
		source = "".join(fs.readlines())
		fs.close()
		return source
	except :
		Printer.showerr(
			"can't open file ", filename,
			"\ncheck if it exists"
		)
		exit()
