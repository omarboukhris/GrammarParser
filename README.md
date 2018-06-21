# GrammarParser
Algebraic (type 2) Grammar parser 

No dependencies required (yet?)

## References :

[1] Lange, Martin; Leiß, Hans (2009). "To CNF or not to CNF? An Efficient Yet Presentable Version of the CYK Algorithm". 

## V 0.1 :

- **graph encoder for generic textual context-free grammars (CFG)**

Let G be a CFG, such as G = (NT, T, Pr, AXIOM) with

* NT    : Set of non terminals
* T     : Set of terminals (alphabet)
* Pr    : Set of production rules ⊆ NT×(NT ∪ T)*, ∪ being the union operator and * the Kleen star operator
* AXIOM : The start symbol

example :

Let G = ({S}, {a,b}, {R1}, AXIOM) be a CFG such as :

R1 : S → a S b | ε

The language described by the grammar is L(G) = { a<sup>n</sup>b<sup>n</sup> }.

dummygrammar.grm
```javascript
AXIOM -> S //this is a comment
S -> //S is a non terminal.
    a. S b. | // This is a production rule, '|' is the OR operator
    '' // epsilone/empty production rule
a.("a") //terminals/tokens are regex for efficiency/convenience purposes 
b.("b") //{a., b.} are terminals
```

testencoder.py
```python
#import important stuff
from parselib.grammarparser import GenericGrammarParser

#load grammar file
fstream = open ("dummygrammar.grm", "r")
txtgrammar = "".join(fstream.readlines())
fstream.close ()

#create parser object
gramparser = GenericGrammarParser ()
grammar = gramparser.parse (txtgrammar) #, verbose=True) #you can make the parser talk

print (grammar)	#print result
```
Results on display :
```javascript
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
- **Operators for grammar transformation ...**
...to Chomsky Normal Form (or any other less restricted normal form, like 2NF)
	- TERM : creates production rule pointing to a specific terminal for each terminal in a production rule
	- BIN  : binarize all rules
	- DEL  : eliminates epsilone rules (grammar must be binned)
	- UNIT : eliminates unit rules (grammar must be binned)

Note : START operator is forced by the language by the AXIOM keyword

example :

testcnf.py 
```python
from parselib.normoperators import TERM, BIN, DEL, UNIT

def getnormalform (grammar) :
	production_rules = grammar.production_rules
	term = TERM (production_rules) # creates operator
	term.apply () # process the rules
	bins = BIN (term.production_rules) # ...
	bins.apply ()
	dels = DEL (bins.production_rules)
	dels.apply ()
	unit = UNIT (dels.production_rules)
	unit.apply ()
	grammar.production_rules = unit.production_rules
	return grammar
	
grammar = getnormalform (grammar)
print (grammar)
```
Result on display :
```javascript
RULE AXIOM = [
	S(NONTERMINAL)
]
RULE S = [
	a.(NONTERMINAL) + S-b(NONTERMINAL)
]
RULE S-b = [
	S(NONTERMINAL) + b.(NONTERMINAL)
	b(TERMINAL)
]
RULE a. = [
	a(TERMINAL)
]
RULE b. = [
	b(TERMINAL)
]

TOKEN a = regex('a')
TOKEN b = regex('b')
```
- **LL(deprecated) and CYK parsers for grammars in CNF**

```python
#import the good stuff
from parselib.parsers import LLParser as LL, CYKParser as CYK

# ... load, parse and normalize grammar

langraph = CYKParser (grammar) # or ...
#langraph = LLParser (grammar)

#load source to parse
TokCode = Tokenizer(grammar.langtokens) #langtokens are language tokens parsed from the file (the regex'es)
TokCode.parse (litterature) # tokenize source code
word = TokCode.tokenized

# this is where the magic happens
x = langraph.wordinlanguage (word) 
```
x is false if *word* is not contained in the language, otherwise can unfold an *experimental* parse tree (that has yet to be improved).

## V 0.2 : (in progress)

Dummy example for language use to parse a subset of C++
```javascript
// example of unambiguous grammar that should be read by the generator

AXIOM -> classes.gen

//list is a primitive function
//we save a list of dataclass 
//.gen or .g means the saved entity will be used by the generator
classes.lab = "classes"
classes.gen = classes(list(dataclass.gen)) 
// similar to : classes -> dataclass.gen classes | '' but in generator syntax

//.lab refers to label
dataclass.lab = "classname", "members" // every label have to be used in the rule
dataclass.g = classdecl. classname(identifier) lcrch. members(list(member.gen)) rcrch. semic.

//["..."] operator is used for "bifurcated" rules like here
// a class is a list of methods and attributes, but each of them has a specific set of parameters
// similar to : member -> attrib | method
member.lab = "content"
member.g["attrib"] = content(attrib.gen)
member.g["method"] = content(method.gen)

//str is a primitive function, like list
//it concatenates in a string whatever the rule between () parses
attrib.lab = "typename", "attribname"
attrib.g = typename(str(attrtype)) attribname(identifier) semic.

method.lab = "typename", "methodname", "params"
method.g = typename(str(methtype)) methodname(identifier) lpar. params(str(listparams)) rpar. semic.

//production rules written in régular grammar
attrtype -> 
	isconst. type. ispointer |
	isconst. identifier. rchev. listtemplatetype lchev. ispointer

methtype ->
	type. ispointer |
	template. rchev. listtemplatedecl lchev. type. ispointer 

listtemplatetype -> 
	identifier. |
	identifier. comma. listtemplatetype

listtemplatedecl ->
	tempdecl. identifier. |
	tempdecl. identifier. comma. listtemplatedecl

ispointer -> 
	pointer. ispointer |
	''

// tokens
//keywords
pointer.("\*")
isconst.("(const)?")
type.("(char|int|float|double)")
visib.("(public|private|protected)")
template.("template")
classdecl.("class")

//operators
lcrch.("\{")
rcrch.("\}")
semic.("\;")
comma.("\,")
lpar.("\(")
rpar.("\)")
lchev.("\<")
rchev.("\>")

//variables and whatever
identifier.("[a-z_A-Z]\w*")
```

