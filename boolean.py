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

"""smt.bitvector

Types and functions for bitvector logic.
"""


from smt.enums import *
from smt.utils import *


class Expression(object):
    
    __slots__ = ['smt2_cache', 'hash_cache']
    
    symbolic = True
    
    def __init__(self):
        self.smt2_cache = None
        self.hash_cache = None

    def __hash__(self):
        if self.hash_cache is None:
            self.hash_cache = string_hash(self.smt2())
        return self.hash_cache

    def smt2(self):
        if self.smt2_cache is None:
            self.smt2_cache = self._smt2()
        return self.smt2_cache

    def __eq__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(self.value == other.value)
        else:
            return BinaryOperation(self, BinaryOperator.Equal, other)

    def __ne__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(self.value != other.value)
        else:
            equal = (self == other)
            return UnaryOperation(UnaryOperator.Not, equal)

    def __and__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(self.value & other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.And, other)

    def __xor__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(self.value ^ other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.Xor, other)

    def __or__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(self.value | other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.Or, other)
    
    def __neg__(self, other):
        if isinstance(self, Constant):
            return Constant(not self.value) 
        else:
            return UnaryOperation(UnaryOperator.Not, self)


class Constant(Expression):
    
    __slots__ = ['value', 'smt2_cache', 'hash_cache']
    
    symbolic = False
    
    def __init__(self, value):
        Expression.__init__(self)
        self.value = value

    def _smt2(self):
        if self.value:
            return 'true'
        else:
            return 'false'

    def symbols(self):
        return set()


class Symbol(Expression):
    
    __slots__ = ['name', 'smt2_cache', 'hash_cache']
    
    def __init__(self, name):
        Expression.__init__(self)
        self.name = name

    def _smt2(self):
        return self.name
    
    def symbols(self):
        return set([self])


class UnaryOperation(Expression):
    
    __slots__ = ['op', 'value', 'smt2_cache', 'hash_cache']
    
    def __init__(self, op, value):
        Expression.__init__(self)
        self.op = op
        self.value = value

    def _smt2(self):
        if self.op != UnaryOperator.Not:
            raise InvalidExpression(self)
        return '(not {0})'.format(self.value.smt2())
    
    def symbols(self):
        return self.value.symbols()


class BinaryOperation(Expression):
    
    __slots__ = ['lhs', 'op', 'rhs', 'smt2_cache', 'hash_cache']
    
    operators = {
        BinaryOperator.And:'and',
        BinaryOperator.Or:'or',
        BinaryOperator.Xor:'xor',
        BinaryOperator.Implies:'=>',
        BinaryOperator.Equal:'=',
    }
    
    def __init__(self, lhs, op, rhs):
        Expression.__init__(self)
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        
    def _smt2(self):
        return '({0} {1} {2})'.format(self.operators[self.op], self.lhs.smt2(), self.rhs.smt2())
        
    def symbols(self):
        return self.lhs.symbols().union(self.rhs.symbols())


class IfThenElse(Expression):
    
    __slots__ = ['predicate', 'if_case', 'else_case', 'smt2_cache', 'hash_cache']
    
    def __init__(self, predicate, if_case, else_case):
        Expression.__init__(self)
        self.predicate = predicate
        self.if_case = if_case
        self.else_case = else_case
    
    def _smt2(self):
        return '(ite {0} {1} {2})'.format(self.predicate.smt2(), self.if_case.smt2(), self.else_case.smt2())
        
    def symbols(self):
        return self.predicate.symbols().union(self.if_case.symbols()).union(self.else_case.symbols())
