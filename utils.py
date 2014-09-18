# -*- coding: utf-8 -*-

#    Copyright 2014 Mark Brand - c01db33f (at) gmail.com
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""smt.utils

A load of useful things that didn't fit anywhere else.
"""

try:
    import pyhashxx
    
    def string_hash(string):
        return pyhashxx.hashxx(string.encode('utf8'))
except:
    def string_hash(string):
        output = 0
        for char in string:
            output = 101 * output + ord(char)
            output &= 0xffffffffffffffff
        return output

try:
    from termcolor import colored
except:
    def colored(*args):
        return args[0]

import re


def carry_bit(size):
    """The mask required for the carry bit on a computation with a
    result of bit-size 'size'.
    """

    return 1 << size


def sign_bit(size):
    """The mask required for the sign bit of a value with bit-size
    'size'.
    """

    return 1 << (size - 1)


def mask(size):
    """The basic bitmask to extract the value of bit-size 'size'."""

    if size == 8:
        return 0xff
    elif size == 16:
        return 0xffff
    elif size == 32:
        return 0xffffffff
    elif size == 64:
        return 0xffffffffffffffff
    elif size == 128:
        return 0xffffffffffffffffffffffffffffffff

    raise ValueError(size)

    
def name(o):
    return o.__class__.__module__ + '.' + o.__class__.__name__


class SolverError(Exception):
    z3_re = re.compile('''line (\d+) column (\d+)\: ([^\n]+)''')
    
    def __init__(self, error, formula):
        self.error = error
        self.formula = formula
            
    def __str__(self):
        match = self.z3_re.search(self.error)
        if match is not None:
            line = int(match.group(1)) - 1
            char = int(match.group(2)) - 1
            lines = self.formula.split('\n')
            bad = lines[line]
            bad = colored(bad[:char], 'blue') + colored(bad[char], 'red') + colored(bad[char+1:], 'blue')
            return 'Solver error: {0}\n{1}'.format(match.group(3), bad)
        else:
            return 'Solver error: {0}'.format(self.error)


class InvalidExpression(Exception):
    
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return 'Invalid expression: {0}'.format(repr(self.expr))
