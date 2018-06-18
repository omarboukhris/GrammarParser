# GrammarParser
Algebraic (type 2) Grammar parser 

No dependencies required (yet?)

# V 0.1 :
## graph encoder for generic textual context-free grammars (CFG) 
Let G be a CFG, such as G = (NT, T, Pr, AXIOM) with :
    - NT    : Set of non terminals
    - T     : Set of terminals (alphabet)
    - Pr    : Set of production rules NTx(NT U T)*, U being the union operator and * the Kleen star operator
    - AXIOM : The start symbol

example :

dummygrammar.grm
```javascript
AXIOM -> S //this is a comment
S -> //S is a non terminal.
    a. S b. | // This is a production rule, '|' is the OR operator
    '' // epsilone/empty production rule
a.("a") //terminals/tokens can be written as regex 
b.("b") //{a., b.} are terminals
```

testencoder.py
```python
#import important stuff
from parselib.grammarparser	import GenericGrammarParser

#load grammar file
fstream = open ("dummygrammar.grm", "r")
txtgrammar = "".join(fstream.readlines())
fstream.close ()

#create parser object
gramparser = GenericGrammarParser ()
grammar = gramparser.parse (txtgrammar) #, verbose=True) #you can make the parser talk

print (grammar)	#print result
```
Results :
```
RULE AXIOM = [
	S(NONTERMINAL)
]
RULE S = [
	a(TERMINAL) + S(NONTERMINAL) + b(TERMINAL)
	''(EMPTY)
]

TOKEN a = regex('a')
TOKEN b = regex('b')
```


 * 
