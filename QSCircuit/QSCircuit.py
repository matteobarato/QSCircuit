#!/usr/bin/env python
import pyparsing as pp
import re

class Ancilla:
    """Ancilla qbit used in reversible gates.
    Attributes:
        position (int): position occupied in the circuit's inputs.
        value (int): value of ancilaa qbit.
        QSCircuit (QSCircuit): instance of QSCircuit: where ancilla qbit will added.
    Args:
        QSCircuit (QSCircuit): instance of QSCircuit: where ancilla qbit will added.
    """
    value = 0
    n_args = 0
    position = 0
    QSCircuit = None

    @staticmethod
    def isAncilla(qubit):
        """Check if qubit is an ancilla qubit.
        Args:
            qubit(string): input of QSCircuit
        Reutrns:
            bool: True if is ancilla qubit, False otherwise.
        """
        return not bool(re.match(r'(^x\d+$)', qubit ))

    def __init__(self, QSCircuit):

        self.QSCircuit = QSCircuit
        pass

    def set(self, value):
        self.position = self.QSCircuit.increase_input()
        self.value = value
        if value == 1:
            self.QSCircuit.add_to_circuit('~',self.pos())
        return self.pos()

    def pos(self):
        return str(self.position)

class QSCircuit:
    """Quantum Script Circuit generator from booelan's logic functions using NCT libary (Not, CNOT, Toffoli)"""
    dim_register = 0
    function = 0
    optimized = False
    Gates = ['~','&','|','^']
    results = []

    def __init__(self, starting_dim_register=0):
        self.dim_register = starting_dim_register

    def is_valid_input(self, qubit):
        """Check if qubit is a boolean logic's valid input
        Args:
            qubit(string): input of QSCircuit
        Reutrns:
            bool: True if is ancilla qubit, False otherwise.
        """
        return bool(re.match(r'(^x\d+$)', qubit))

    def increase_input(self):
        """Increase the register size for the next input qubit"""
        self.dim_register += 1
        return self.dim_register

    def setOptimize(self, value):
        """Increase the register size for the next input qubit
        Note:
            If actived, optimizes the insertion of the quatistic gates and ancilla qubits to generate a smaller circuit.
        Args:
            value(boolean): True able quantum circuit optimization, False disable.
        Todo:
            optimize the optimizer.
        """
        self.optimized = value

    def add_to_circuit(self, op, first, second = None, ancilla=None):
        """Add correspondent quantum gates to circuit
        Note:
            If was called `setOptimize(True)` the function will optimized.
            Only when `ancilla.set()` is called, the ancilla qubit will added to circuit.
        Args:
            op(string): Classic port.
            first(string): Position of first input.
            second(string): Position of second input.
            ancilla(Ancilla): ancilla qubit that will used in.
        Return:
            string: Positon of gate's output
        """
        if not ancilla: ancilla= Ancilla(self)

        if op in self.Gates:
            if op=='~':
                if (self.optimized):
                    # if it is an ancilla we can override its value
                    if (Ancilla.isAncilla(first)):
                        self.results.append(['SigmaX', first])
                        return first
                ancilla_pos = ancilla.set(1)
                self.results.append(['CNot', first, ancilla_pos])
                return ancilla_pos

            elif op=='&':
                ancilla_pos = ancilla.set(0)
                self.results.append(['Toffoli', first, second, ancilla_pos])
                return ancilla_pos

            elif op=='^':
                if (self.optimized):
                    # if it is an ancilla we can override its value
                    if (Ancilla.isAncilla(first)):
                        self.results.append(['CNot', second, first])
                        return first
                    elif (Ancilla.isAncilla(second)):
                        self.results.append(['CNot', first, second])
                        return second
                ancilla_pos = ancilla.set(0)
                self.results.append(['CNot', first, ancilla_pos])
                self.results.append(['CNot', second, ancilla_pos])
                return ancilla_pos

            elif op=='|':
                ancilla_pos = ancilla.set(0) # QUESTION: verificare se si puo fare di meglio
                self.results.append(['Toffoli', first, second, ancilla_pos])
                self.results.append(['CNot', first, ancilla_pos])
                self.results.append(['CNot', second, ancilla_pos])
                return ancilla_pos
        else:
            print ('QSCircuit ERROR: '+str(op)+ ' -> invalid gate. Classic gates supported: '+str(Gates))
            return None

    def set_input(self, function):
        """Transform a boolean function into hierarchical nested list of operations.
            Required pyparsing module: https://pypi.org/project/pyparsing/
        Args:
            function(string): Boolean function. If not function
        Return:
            Lisdt: Return hierarchical nested list of operations like a tree. Use `-v --verbose` for print it
        """
        if not self.dim_register or self.dim_register == 0: #get max value input es. " (x1 ^ x2 | x5) ^ ~x3 " -> 5
            max_position_input = max(map(lambda x: int(x[1:]), re.findall(r'x\d+', function)))
            self.dim_register = self.dim_register+max_position_input
            self.n_args = max_position_input

        number = pp.Regex(r'(^x\d+$)')
        identifier = pp.Word(pp.alphanums+'x'+'_')
        comparison_term = identifier | number
        condition = pp.Group(comparison_term)

        expr = pp.operatorPrecedence(condition,[
                                    (self.Gates[0], 1, pp.opAssoc.RIGHT, ), # ~
                                    (self.Gates[1], 2, pp.opAssoc.LEFT, ),  # &
                                    (self.Gates[2], 2, pp.opAssoc.LEFT, ),  # |
                                    (self.Gates[3], 2, pp.opAssoc.LEFT, ),  # ^
                                ])
        pp.ParserElement.enablePackrat()
        self.operations_list = expr.parseString(function).asList()
        return self.operations_list

    def convert(self):
        """Supporting function for call `dfs_convert`
        Args:
            see `dfs_convert`.
        Return:
            see `dfs_convert`.
        """
        return self.dfs_convert(self.operations_list)

    def dfs_convert(self, ops_list=None):
        """Convert list of operations (result of `self.set_input` function) into a quantum circuit.
        Perform a DFS (depth-first search) on ops_list.
        Note:
            quantum circuit returned is a sequnce of `QScript` quantum gates.
        Args:
            function(operations_list): list of operations.
        Return:
            list: quantum circuit operations.
        """
        if not isinstance(ops_list, list):
            return ops_list
        if len(ops_list) == 1 : # [ $ ]
            return self.dfs_convert(ops_list[0])


        if len(ops_list) == 2 : # [ ~ $ ]
            r = self.dfs_convert(ops_list[1])
            op = ops_list[0]
            return self.add_to_circuit(op, r, None)
        else:
            inputs = []
            ancilla_res = Ancilla(self)
            for val in ops_list:
                inputs.append(self.dfs_convert(val))
                if len(inputs) >= 3 :
                    if self.optimized and (inputs[1]=='&' or inputs[1]=='^'):
                        tmp_pos = self.add_to_circuit( inputs[1],inputs[2], inputs[0])
                    else:
                        tmp_pos = self.add_to_circuit( inputs[1],inputs[2], inputs[0], ancilla_res)
                    inputs = [tmp_pos]
            return inputs[0]

    def print_circuit(self):
        """Print a quantum circuit scheme from converted quantum circuit"""
        operations = self.asList()
        res = [[] for i in range(len(operations)+1)] # len(operations)+1 for column of header
        for h_index, val in enumerate(operations):
            # add starter index of qbit's register
            space = ""
            for i in range(2- ((h_index+1)/10)):
                space += " "
            if h_index < self.n_args :
                res[0].append('|x'+str(h_index+1)+'> '+space)
                res[0].append("       ")
            else:
                res[0].append('|0>    ')
                res[0].append("       ")

        for index, val in enumerate(operations):
            # push in res list correspondent symbols of current gate operation
            find = False    # flag for add "|" trace in circuit scheme
            inputs = []     # list of inputs's positions in current gate
            output = ''     # output's position
            if val[0] == 'Toffoli':
                # ['Toffoli', first, second, output]
                inputs.append(int(val[1]) if Ancilla.isAncilla(val[1]) else int(val[1][1:]))
                inputs.append(int(val[2]) if Ancilla.isAncilla(val[2]) else int(val[2][1:]))
                output = int(val[3])

            if val[0] == 'CNot':
                # ['CNot', first, output]
                inputs.append(int(val[1]) if Ancilla.isAncilla(val[1]) else int(val[1][1:]))
                output = int(val[2])

            if val[0] == 'SigmaX':
                # ['SigmaX', output]
                output = int(val[1])

            for i in range(1,self.dim_register+1): # remember the column of header
                if i in inputs:
                    res[index+1].append('--X--')
                    find = True
                elif i == output:
                    res[index+1].append('--O--')
                    find = False
                elif find:
                    res[index+1].append('--|--')
                else:
                    res[index+1].append('-----')
                if find:
                    res[index+1].append('  |  ')
                else:
                    res[index+1].append('     ')
        # transposed res list for print circuit scheme in correct order
        for j in range(0,self.dim_register*2):
            line = ""
            for z in range(0,len(res)):
                line+=res[z][j]
            print (line)

    def get_regiser_size(self):
        """Return actual register size of quantum circuit"""
        return self.dim_register

    def asList(self):
        """Return converted quantum circuit as list of quantum gates"""
        return self.results

    def asString(self):
        """Return converted quantum circuit as string of quantum gates"""
        return '; '.join(map(lambda x: x[0]+' '+(', '.join(x[1:])), self.results))+';   '
