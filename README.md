## Grammar parselib

This is intended to be a simple yet "efficient" (as efficient as Python can be) framework for context free grammar (CFG) parsing.

Can be used to code a symbolic mathematical kernel, a source-to-source transcompiler or whatever.. The sky is the limit (along with the established expressive power of type 2 grammars)

No dependencies required (yet?)

### References :

[1] Lange, Martin; Leiß, Hans (2009). "To CNF or not to CNF? An Efficient Yet Presentable Version of the CYK Algorithm". 

### Grammars :

Let G be a CFG, such as G = (NT, T, Pr, AXIOM) with

* NT    : Set of non terminals
* T     : Set of terminals (alphabet)
* Pr    : Set of production rules ⊆ NT×(NT ∪ T)*, ∪ being the union operator and * the Kleen star operator
* AXIOM : The start symbol

example :

Let G = ({S}, {a,b}, {R1}, AXIOM) be a CFG such as :

R1 : S → a S b | ε

The language described by the grammar is L(G) = { a<sup>n</sup>b<sup>n</sup> }.

written following the parselib convention in a text file would look like :

```javascript
AXIOM -> S //this is a comment
S -> //S is a non terminal.
    a. S b. | // This is a production rule, '|' is the OR operator
    '' // epsilone/empty production rule
a.("a") //terminals/tokens are regex for efficiency/convenience purposes 
b.("b") //{a., b.} are terminals
```

### Main interface :

All functions mentioned later and more are wrapped in a utility class (`parselib.parselibinstance.ParselibInstance`).

Reading a grammar and parsing a source code then becomes trivial :
```python
from parselib.parselibinstance import ParselibInstance

parseinst = ParselibInstance ()

parseinst.loadGrammar("data/grammar.grm", verbose=True)
parsedDataStruct = parseinst.processSource("data/test.java") #any source code
```
This can mainly be useful to setup a transcompiling framework.

## Grammar's syntax

### Terminals

Every terminal node can be written as a regex `terminalnodename.("w*")`.
They are used in production rules like `terminalnodename.`

### Non terminals

Non terminals are defined in a grammar as non terminal node.
As an example :
```javascript
nonterminal -> nonterm1 nonterm2 term. | term.
```
Here we define a non terminal node named `nonterminal` as the concatenation of non terminal nodes `nonterm1, nonterm2` and a terminal node `term.`. 

`term.` alone is also accepted.

### Labeling operators :

Each operand associated with the operators `!` or `label=` in a production rule tells the parser to save the data in a data structure formed by the production rule non terminals.

Example :
let S=(a S b | eps) our grammar. We want to save each parsed `S` in a data structure containing the informations we need from S. 
We write the grammar as follows :
```javascript
S -> 
	!a. S_child=S !b. | 
	''
```
This generates a data structure similar to this 
```c++
struct S {
	string a ;
	struct S S_child ;
	string b ;
} ;
```
in which a correctly parsed source code will eventually be stored.

### Lists :

`list` operators have been implemented in the grammar's accepted syntax.
Example :
```javascript
aListNode ->
	element1. element2. anotherNode |
aListNode aListNode | '' //this line define the node as a list
```
Can become
```javascript
aListNode ->
	element1. element2. anotherNode |
__list__ // [] is also accepted
```
The list operator basically generates a rule to be used as a loop guard for the list parsing.

### Import :

It is possible to break a grammar in submodules, importable using :
```javascript
%import "submodule.grm"

AXIOM -> //...
```
The preprocessor is protected against nested imports.
NOTE:Doesn't support path yet

### Str :

If you want to convert a non terminal node's value to str instead of catching a strucutre, the `s:` operator can be used to convert the node to a string.
```javascript
//...
someHeader -> s:complexNodeToConvert theRestofit | '' //...
```
This is mainly to catch strings that regexs can't.

## Under the hood

### Graph encoder for generic textual CFG

```python
#import important stuff
from parselib.parsers.grammarparser import GenericGrammarParser

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
### Operators for grammar transformation 

to Chomsky Normal Form (or any other less restricted normal form, like 2NF<sup>[1]</sup>)

- TERM : creates production rule pointing to a specific terminal for each terminal in a production rule
- BIN  : binarize all rules
- DEL  : eliminates epsilone rules (grammar must be binned)
- UNIT : eliminates unit rules (grammar must be binned)

Note : START operator is forced by the language by the AXIOM keyword

```python
from parselib.operations.normoperators import TERM, BIN, DEL, UNIT

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
### CYK parsers for grammars in 2NF<sup>[1]</sup>

```python
#import the good stuff
from parselib.parsers.parsers import CYKParser as CYK
from parselib.operations.normoperators import get2nf
# ... load, parse and normalize grammar

#CNF is deprecated for CYK parser
grammar = get2nf (grammar)

langraph = CYK (grammar) 

#tokenizer to transform source code to tokens
TokCode = Tokenizer(grammar.tokens) 
#grammar.tokens are language tokens parsed from the file (the regex'es)

#load source to parse
litterature = "some word for membership checking in full text"
TokCode.parse (litterature) # tokenize source code

# this is where the magic happens
x = langraph.membership (TokCode.tokenized) 
```
x is false if *word* is not contained in the language, otherwise can unfold a parse tree





