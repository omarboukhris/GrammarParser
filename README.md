# Grammar parselib

This is intended to be a simple yet "efficient" (as efficient as Python can be) framework for context free grammar (CFG) parsing.

Can be used to code a symbolic mathematical kernel, a source-to-source transcompiler or whatever.. The sky is the limit (along with the established expressive power of type 2 grammars)

No dependencies required (yet?)

## References :

[1] Lange, Martin; Leiß, Hans (2009). "To CNF or not to CNF? An Efficient Yet Presentable Version of the CYK Algorithm". 

## Grammar definition syntax :

Let G be a CFG, such as G = (NT, T, Pr, AXIOM) with

* NT    : Set of non terminals
* T     : Set of terminals (alphabet)
* Pr    : Set of production rules ⊆ NT×(NT ∪ T)*, ∪ being the union operator and * the Kleen star operator
* AXIOM : The start symbol

example :

Let G = ({S}, {a,b}, {R1}, AXIOM) be a CFG such as :

R1 : S → a S b | ε

The language described by the grammar is L(G) = { a<sup>n</sup>b<sup>n</sup> }.

* Grammar Syntax V 0.1 : dummygrammar.grm

```javascript
AXIOM -> S //this is a comment
S -> //S is a non terminal.
    a. S b. | // This is a production rule, '|' is the OR operator
    '' // epsilone/empty production rule
a.("a") //terminals/tokens are regex for efficiency/convenience purposes 
b.("b") //{a., b.} are terminals
```

## Graph encoder for generic textual CFG

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
## Operators for grammar transformation ...

...to Chomsky Normal Form (or any other less restricted normal form, like 2NF<sup>[1]</sup>)

- TERM : creates production rule pointing to a specific terminal for each terminal in a production rule
- BIN  : binarize all rules
- DEL  : eliminates epsilone rules (grammar must be binned)
- UNIT : eliminates unit rules (grammar must be binned)

Note : START operator is forced by the language by the AXIOM keyword

example :

testcnf.py 
```python
from parselib.normoperators import TERM, BIN, DEL, UNIT

def getcnf (grammar) :
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
	
grammar = getcnf (grammar)
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
- **LL(deprecated) and CYK parsers for grammars in CNF and 2NF<sup>[1]</sup>**

```python
#import the good stuff
from parselib.parsers       import CYKParser as CYK
from parselib.normoperators	import get2nf
# ... load, parse and normalize grammar

grammar = get2nf (grammar)

langraph = CYK (grammar) 

#tokenizer to transform source code to tokens
TokCode = Tokenizer(grammar.tokens) 
#grammar.tokens are language tokens parsed from the file (the regex'es)

#load source to parse
litterature = "some word for membership checking in full text"
TokCode.parse (litterature) # tokenize source code
word = TokCode.tokenized

# this is where the magic happens
# in CNF, 2NF example to come
x = langraph.membership (word) 
```
x is false if *word* is not contained in the language, otherwise can unfold a parse tree.
Should be linearly reparsed to plug data in the accurate data structure

## To come : pipeline for language processing

## V 0.2 : 

# Operators :






