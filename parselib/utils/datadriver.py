import parselib.utils.io as io 
import sqlite3

### play with this

create_table_query = """
CREATE TABLE {tablename} (
	ID INT PRIMARY KEY NOT NULL,
	{columns}
) ;
"""

class DataDriver :
	
	def __init__ (self, datastructures, location=":memory:") :
		self.connx = sqlite3.connect(location)
		self.datastructures = datastructures.keeper
		self.processed = []
		self.fklist = []
		if "all" in self.datastructures.keys() :
			del self.datastructures["all"]
		
	def deploy (self) :
		self.processed = []
		self.fklist = []
		
		#self.execute_query("PRAGMA foreign_keys=on;")

		for tablename, columns in self.datastructures.items() :
			
			self.create_table (tablename, columns)
		
		for fk in self.fklist :
			print (fk)
			self.execute_query (fk)
			

	def isTableCreated (self, tablename) :
		return tablename in self.processed 
		
	def create_table (self, tablename, columns) :
		if self.isTableCreated (tablename) :
			return
		self.processed.append (tablename)
		
		strcolumns = ["PARENT_ID INT"]
		for i in range (len(columns)) :
			if columns[i] in self.datastructures.keys() :
				#if FOREIGN KEY
				#add column "parent" to child table
				pass
			else :
				strcolumns.append(columns[i] + " STR")
			
		query = create_table_query.format (
			tablename=tablename, 
			columns=",\n\t".join(strcolumns)
		)
		
		print (query)
		self.execute_query (query)
	
	def execute_query (self, query) :
		if sqlite3.complete_statement(query):
			try:
				self.connx.execute (query)
				io.Printer.showinfo ("Successfully executed query")
			except sqlite3.Error as e:
				io.Printer.showerr("An sqlite3 error occurred:", e.args[0])
				exit ()

		



