
class Printer :
	
	@staticmethod
	def showinfo (*ss) :
		print ("[info] ", *ss)
	
	@staticmethod
	def showerr (*ss) :
		print ("[error] ", *ss)

def gettextfilecontent (filename):
	fs = open(filename, "r")
	source = "".join(fs.readlines())
	fs.close()
	return source