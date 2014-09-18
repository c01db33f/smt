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

"""smt.enums

Shared enumerations.
"""


class UnaryOperator(object):
    Not = 0
    Negate = 1


class BinaryOperator(object):
    And = 0
    Or = 1
    Implies = 2
    
    Nand = 3
    Nor = 4
    Xor = 5
    Xnor = 6
    Add = 7
    Multiply = 8
    UnsignedDivide = 9
    UnsignedRemainder = 10
    Subtract = 11
    SignedDivide = 12
    SignedRemainder = 13
    SignedModulo = 14
    ShiftLeft = 15
    LogicalShiftRight = 16
    ArithmeticShiftRight = 17
    RotateLeft = 18
    RotateRight = 19
    
    UnsignedLessThan = 20
    Equal = 21
    UnsignedLessThanOrEqual = 22
    UnsignedGreaterThan = 23
    UnsignedGreaterThanOrEqual = 24
    SignedLessThan = 25
    SignedLessThanOrEqual = 26
    SignedGreaterThan = 27
    SignedGreaterThanOrEqual = 28


class ExtensionKind(object):
    Zero = 0
    Sign = 1
