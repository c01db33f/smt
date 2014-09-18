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

import smt.boolean as bl

from smt.enums import *
from smt.utils import *


class Expression(object):
    
    __slots__ = ['size', 'smt2_cache', 'hash_cache']
    
    symbolic = True
    
    def __init__(self, size):
        self.size = size
        self.smt2_cache = None
        self.hash_cache = None
        
    def __str__(self):
        if self.symbolic:
            return 'symbolic'
        else:
            return 'concrete'
            
    def smt2(self):
        if self.smt2_cache is None:
            self.smt2_cache = self._smt2()
        return self.smt2_cache

    def __hash__(self):
        if self.hash_cache is None:
            self.hash_cache = string_hash(self.smt2())
        return self.hash_cache

    def __lt__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return bl.Constant(self.value < other.value)
        elif isinstance(self, Constant) and isinstance(other, int):
            return bl.Constant(self.value < other)
        elif isinstance(other, int):
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedLessThan, Constant(self.size, other))
        else:
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedLessThan, other)

    def __le__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return bl.Constant(self.value <= other.value)
        elif isinstance(self, Constant) and isinstance(other, int):
            return bl.Constant(self.value <= other)
        elif isinstance(other, int):
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedLessThanOrEqual, Constant(self.size, other))
        else:
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedLessThanOrEqual, other)

    def __eq__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return bl.Constant(self.value == other.value)
        elif isinstance(self, Constant) and isinstance(other, int):
            return bl.Constant(self.value == other)
        elif isinstance(other, int):
            return BooleanBinaryOperation(self, BinaryOperator.Equal, Constant(self.size, other))
        else:
            return BooleanBinaryOperation(self, BinaryOperator.Equal, other)

    def __ne__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return bl.Constant(self.value != other.value)
        elif isinstance(self, Constant) and isinstance(other, int):
            return bl.Constant(self.value != other)
        else:
            equal = (self == other)
            return bl.UnaryOperation(UnaryOperator.Not, equal)

    def __gt__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return bl.Constant(self.value > other.value)
        elif isinstance(self, Constant) and isinstance(other, int):
            return bl.Constant(self.value > other)
        elif isinstance(other, int):
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedGreaterThan, Constant(self.size, other))
        else:
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedGreaterThan, other)

    def __ge__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return bl.Constant(self.value >= other.value)
        elif isinstance(self, Constant) and isinstance(other, int):
            return bl.Constant(self.value >= other)
        elif isinstance(other, int):
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedGreaterThanOrEqual, Constant(self.size, other))
        else:
            return BooleanBinaryOperation(self, BinaryOperator.UnsignedGreaterThanOrEqual, other)

    def __add__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value + other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.Add, other)

    def __sub__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value - other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.Subtract, other)

    def __mul__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value * other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.Multiply, other)

    def __floordiv__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value // other.value)
        else:
            return BinaryOperation(self, BinaryOperator.UnsignedDivide, other)

    def __mod__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value % other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.UnsignedRemainder, other)

    def __lshift__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value << other.value) 
        else:
            return BinaryOperation(self, BinaryOperator.ShiftLeft, other)
            
    def __rshift__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            # force value to be unsigned
            value = self.value % carry_bit(self.size)
            # now check the sign bit
            if value & sign_bit(self.size):
                value = -carry_bit(self.size) + value

            return Constant(max(self.size, other.size), value >> other.value)
        else:
            return BinaryOperation(self, BinaryOperator.ArithmeticShiftRight, other)

    def __and__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value & other.value)
        else:
            return BinaryOperation(self, BinaryOperator.And, other)

    def __xor__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value ^ other.value)
        else:
            return BinaryOperation(self, BinaryOperator.Xor, other)

    def __or__(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value | other.value)
        else:
            return BinaryOperation(self, BinaryOperator.Or, other)
    
    def __neg__(self):
        if isinstance(self, Constant):
            return bl.Constant(-self.value) 
        else:
            return UnaryOperation(UnaryOperator.Negate, self)

    def logical_shift_right(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            return Constant(max(self.size, other.size), self.value >> other.value)
        else:
            return BinaryOperation(self, BinaryOperator.LogicalShiftRight, other)
            
    def extract(self, size=None, start=None, end=None):
        assert size is not None or (start is not None and end is not None)

        if isinstance(self, Constant):
            if size is not None:
                end = self.size
            else:
                size = end - start
            value = self.value >> (self.size - end)
            return Constant(size, value)

        else:
            # simplify the case of extracting all of something
            if size is not None and self.size == size:
                return self

            elif (start is not None and end is not None) and (start == 0 and end == self.size):
                return self

            # simplify an extraction from an extension
            if isinstance(self, Extension):
                if end == self.size:
                    size = end - start

                if size is not None:
                    if size == self.value.size:
                        return self.value
                    elif size < self.value.size:
                        return self.value.extract(size=size)
                    else:
                        return Extension(self.value, kind=self.kind, size=size)

            return Extraction(self, size=size, start=start, end=end)
            
    def concatenate(self, other):
        if isinstance(self, Constant) and isinstance(other, Constant):
            value = (self.value << other.size) | other.value
            return Constant(self.size + other.size, value)
        else:
            return concatenate([self, other])
            
    def zero_extend(self, size):
        if isinstance(self, Constant):
            return Constant(self.size + size, self.value)
        else:
            return Extension(self, kind=ExtensionKind.Zero, extension_size=size)
            
    def zero_extend_to(self, size):
        if isinstance(self, Constant):
            return Constant(size, self.value)
        else:
            return Extension(self, kind=ExtensionKind.Zero, size=size)
            
    def sign_extend(self, size):
        if isinstance(self, Constant):
            size = self.size + size
            if self.value & sign_bit(self.size):
                value = mask(self.size) ^ mask(size) | self.value
            else:
                value = self.value
            return Constant(size, value)
        else:
            return Extension(self, kind=ExtensionKind.Sign, extension_size=size)
            
    def sign_extend_to(self, size):
        if isinstance(self, Constant):
            if self.value & sign_bit(self.size):
                value = mask(self.size) ^ mask(size) | self.value
            else:
                value = self.value
            return Constant(size, value)
        else:
            return Extension(self, kind=ExtensionKind.Sign, size=size)
        
    def resize(self, size):
        if self.size < size:
            return self.zero_extend_to(size)
        elif self.size > size:
            return self.extract(size=size)
        else:
            return self

    def can_be_zero(self):
        if isinstance(self, Constant):
            return bl.Constant(self.value == 0)
        else:
            return self == Constant(self.size, 0)
            
    def can_be_nonzero(self):
        if isinstance(self, Constant):
            return bl.Constant(self.value != 0)
        else:
            return self != Constant(self.size, 0)
            

def if_then_else(predicate, if_case, else_case):
    if isinstance(predicate, bl.Constant):
        if predicate.value:
            return if_case
        else:
            return else_case
    else:
        return IfThenElse(predicate, if_case, else_case)

def concatenate(elements):
    # first preprocess any contained concatenations
    final_elements = []
    for element in elements:
        if isinstance(element, Concatenation):
            final_elements += element.elements
        else:
            final_elements.append(element)
        
    # now rebuild chunks of extractions
    reconstruct_value = None
    if isinstance(final_elements[0], Extraction):
        reconstruct_value = final_elements[0].value
        reconstruct_index = 0
        for element in final_elements:
            if isinstance(element, Extraction):
                if (reconstruct_value.size == element.value.size and reconstruct_value == element.value):
                    if element.start == reconstruct_index:
                        reconstruct_index += element.size
                        continue

            reconstruct_value = None
            break
            
    if reconstruct_value is None:
        return Concatenation(final_elements)
    else:
        return reconstruct_value
    
class Constant(Expression):
    
    __slots__ = ['size', 'value', 'smt2_cache', 'hash_cache']
    
    symbolic = False
    
    def __init__(self, size, value):
        Expression.__init__(self, size)
        self.value = value % carry_bit(size)
        
    def __str__(self):
        template = '{:0' + str(self.size // 4) + 'x}'
        return template.format(self.value, '0' + str(self.size // 4) + 'x')

    def _smt2(self):
        return ('#x{0:0' + str(self.size // 4) + 'x}').format(self.value % carry_bit(self.size))

    def symbols(self):
        return set()


class Symbol(Expression):
    
    __slots__ = ['size', 'name', 'smt2_cache', 'hash_cache']
    
    def __init__(self, size, name):
        Expression.__init__(self, size)
        self.name = name

    def _smt2(self):
        return self.name
    
    def symbols(self):
        return set([self])


class UnaryOperation(Expression):
    
    __slots__ = ['size', 'op', 'value', 'smt2_cache', 'hash_cache']
    
    def __init__(self, op, value):
        Expression.__init__(self, value.size)
        self.op = op
        self.value = value

    def _smt2(self):
        if self.op != UnaryOperator.Negate:
            raise InvalidExpression(self)
        return '(bvneg {0})'.format(self.value.smt2())
    
    def symbols(self):
        return self.value.symbols()


class BooleanUnaryOperation(bl.Expression):
    
    __slots__ = ['op', 'value', 'smt2_cache', 'hash_cache']
    
    def __init__(self, op, value):
        bl.Expression.__init__(self)
        self.op = op
        self.value = value

    def _smt2(self):
        if self.op != UnaryOperator.Not:
            raise InvalidExpression(self)
        return '(bvnot {0})'.format(self.value.smt2())
        
    def symbols(self):
        return self.value.symbols()


class BinaryOperation(Expression):
    
    __slots__ = ['size', 'lhs', 'op', 'rhs', 'smt2_cache', 'hash_cache']
    
    operators = {
        BinaryOperator.And:'bvand',
        BinaryOperator.Or:'bvor',
        BinaryOperator.Nand:'bvnand',
        BinaryOperator.Nor:'bvnor',
        BinaryOperator.Xor:'bvxor',
        BinaryOperator.Xnor:'bvxnor',
        BinaryOperator.Add:'bvadd',
        BinaryOperator.Multiply:'bvmul',
        BinaryOperator.UnsignedDivide:'bvudiv',
        BinaryOperator.UnsignedRemainder:'bvurem',
        BinaryOperator.Subtract:'bvsub',
        BinaryOperator.SignedDivide:'bvsdiv',
        BinaryOperator.SignedRemainder:'bvsrem',
        BinaryOperator.SignedModulo:'bvsmod',
        BinaryOperator.ShiftLeft:'bvshl',
        BinaryOperator.LogicalShiftRight:'bvlshr',
        BinaryOperator.ArithmeticShiftRight:'bvashr',
        BinaryOperator.RotateLeft:'bvrol',
        BinaryOperator.RotateRight:'bvror'
    }
    
    def __init__(self, lhs, op, rhs):
        assert lhs.size == rhs.size
        Expression.__init__(self, lhs.size)
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        
    def _smt2(self):
        return '({0} {1} {2})'.format(self.operators[self.op], self.lhs.smt2(), self.rhs.smt2())
        
    def symbols(self):
        return self.lhs.symbols().union(self.rhs.symbols())

class BooleanBinaryOperation(bl.Expression):
    
    __slots__ = ['lhs', 'op', 'rhs', 'smt2_cache', 'hash_cache']
    
    operators = {
        BinaryOperator.UnsignedLessThan:'bvult',
        BinaryOperator.Equal:'=',
        BinaryOperator.UnsignedLessThanOrEqual:'bvule',
        BinaryOperator.UnsignedGreaterThan:'bvugt',
        BinaryOperator.UnsignedGreaterThanOrEqual:'bvuge',
        BinaryOperator.SignedLessThan:'bvslt',
        BinaryOperator.SignedLessThanOrEqual:'bvsle',
        BinaryOperator.SignedGreaterThan:'bvsgt',
        BinaryOperator.SignedGreaterThanOrEqual:'bvsge',
    }

    def __init__(self, lhs, op, rhs):
        assert lhs.size == rhs.size
        bl.Expression.__init__(self)
        self.lhs = lhs
        self.op = op
        self.rhs = rhs
        
    def _smt2(self):
        return '({0} {1} {2})'.format(self.operators[self.op], self.lhs.smt2(), self.rhs.smt2())
    
    def symbols(self):
        return self.lhs.symbols().union(self.rhs.symbols())


class Concatenation(Expression):
    
    __slots__ = ['size', 'elements', 'smt2_cache', 'hash_cache']
    
    def __init__(self, elements):
        size = 0
        self.elements = []
        for element in elements:
            size += element.size
            self.elements.append(element)
        Expression.__init__(self, size)
        
    def _smt2(self):
        output = '(concat '
        for element in self.elements:
            output += ' ' + element.smt2()
        output += ')'
        return output
        
    def symbols(self):
        output = set()
        for element in self.elements:
            output = output.union(element.symbols())
        return output


class Repetition(Expression):
    
    __slots__ = ['size', 'value', 'count', 'smt2_cache', 'hash_cache']
    
    def __init__(self, value, count):
        Expression.__init__(self, value.size * count)
        self.value = value
        self.count = count
        
    def _smt2(self):
        return '((_ repeat {0}) {1})'.format(self.count, self.value.smt2())
    
    def symbols(self):
        return self.value.symbols()


class Extraction(Expression):
    
    __slots__ = ['size', 'value', 'start', 'end', 'smt2_cache', 'hash_cache']
    
    def __init__(self, value, start=None, end=None, size=None):
        assert size is not None or (start is not None and end is not None)
        self.value = value
        if size is not None:
            self.start = 0
            self.end = size
        else:
            self.start = start
            self.end = end
        Expression.__init__(self, self.end - self.start)

    def _smt2(self):
        return '((_ extract {0} {1}) {2})'.format(self.end - 1, self.start, self.value.smt2())

    def symbols(self):
        return self.value.symbols()


class Extension(Expression):
    
    __slots__ = ['size', 'value', 'kind', 'extension_size', 'smt2_cache', 'hash_cache']
    
    kinds = {
        ExtensionKind.Zero:'zero_extend',
        ExtensionKind.Sign:'sign_extend'
    }
    
    def __init__(self, value, kind, size=None, extension_size=None):
        assert size is not None or extension_size is not None

        self.value = value
        self.kind = kind

        if size is not None:
            self.extension_size = size - value.size
            assert self.extension_size > 0
            Expression.__init__(self, size)

        else:
            self.extension_size = extension_size
            assert self.extension_size > 0
            Expression.__init__(self, value.size + extension_size)
        
    def _smt2(self):
        return '((_ {0} {1}) {2})'.format(self.kinds[self.kind], self.extension_size, self.value.smt2())

    def symbols(self):
        return self.value.symbols()


class IfThenElse(Expression):
    
    __slots__ = ['predicate', 'if_case', 'else_case', 'smt2_cache', 'hash_cache']
    
    def __init__(self, predicate, if_case, else_case):
        assert if_case.size == else_case.size
        Expression.__init__(self, if_case.size)
        self.predicate = predicate
        self.if_case = if_case
        self.else_case = else_case
    
    def _smt2(self):
        return '(ite {0} {1} {2})'.format(self.predicate.smt2(), self.if_case.smt2(), self.else_case.smt2())
        
    def symbols(self):
        return self.predicate.symbols().union(self.if_case.symbols()).union(self.else_case.symbols())
