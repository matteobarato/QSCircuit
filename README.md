# Quantum Script Circuit
Quantum circuit generator (for [Quantum Computing Playground](http://www.quantumplayground.net)) from booelan's logic functions using NCT libary (Not, CNOT, Toffoli)

## Supported Classic Gates (C style):
* ~ not
* | or
* & and
* ^ xor

## Installation:
Into project's folder:
```
pip install .
	or
pip install . --user
```
## Usage example:
```
QSCircuit "(x2 & x3 & x4 ) ^ (x2 & x3 & x5 ) ^ (x1 & x2 ) ^ (x3 & x4)  ^ (x4 & x5 ) ^ x3)" -o -v -p
```
Optional arguments:
* *- o* optimize circuit for use less Gates
* *- p* print schema of quantum circuit
* *- v* verbose

 for other info:
```
QSCircuit -h
```

##Examples of linear boolean functions:
* "(x2 & x3 & x4 ) ^ (x2 & x3 & x5 ) ^ (x1 & x2 ) ^ (x3 & x4)  ^ (x4 & x5 ) ^ x3)"\n
* "((($0 & $1) ^ ($0 & $2)) | ($1 &  $2))"\n
* "x0 & x1 & x2 & x4 ^ ~x5"\n
