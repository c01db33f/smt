import itertools

import nose

import bitvector as bv
import boolean as bl
import enums

from solver import *

test_sizes = [8, 16, 32, 64]

test_values = [
    0,
    1,
    -1, 
    0x7f, 
    0xff, 
    0x7fff, 
    0xffff, 
    0x7fffffff, 
    0xffffffff,
    0x7fffffffffffffff,
    0xffffffffffffffff]

def binary_concrete_against_symbolic(function):
    testcases = itertools.product(test_values, test_values, test_sizes)
    for a, b, size in testcases:
        s = Solver()
        
        concrete_a = bv.Constant(size, a)
        concrete_b = bv.Constant(size, b)
        
        symbolic_a = bv.Symbol(size, 'symbolic_a')
        symbolic_b = bv.Symbol(size, 'symbolic_b')

        concrete_result = function(concrete_a, concrete_b)
        symbolic_result = function(symbolic_a, symbolic_b)
        
        s.add(symbolic_a == concrete_a)
        s.add(symbolic_b == concrete_b)
        
        assert not s.check(concrete_result != symbolic_result)

def binary_concrete_against_symbolic_nozero(function):
    testcases = itertools.product(test_values, test_values, test_sizes)
    for a, b, size in testcases:
        
        if b == 0:
            continue
        
        s = Solver()
        
        concrete_a = bv.Constant(size, a)
        concrete_b = bv.Constant(size, b)
        
        symbolic_a = bv.Symbol(size, 'symbolic_a')
        symbolic_b = bv.Symbol(size, 'symbolic_b')

        concrete_result = function(concrete_a, concrete_b)
        symbolic_result = function(symbolic_a, symbolic_b)
        
        s.add(symbolic_a == concrete_a)
        s.add(symbolic_b == concrete_b)
        
        assert not s.check(concrete_result != symbolic_result)

def unary_concrete_against_symbolic(function):
    testcases = itertools.product(test_values, test_sizes)
    for a, size in testcases:

        s = Solver()
        
        concrete_a = bv.Constant(size, a)
        
        symbolic_a = bv.Symbol(size, 'symbolic_a')
        
        concrete_result = function(concrete_a)
        symbolic_result = function(symbolic_a)
        
        s.add(symbolic_a == concrete_a)
        
        assert not s.check(concrete_result != symbolic_result)

def test_lt():
    binary_concrete_against_symbolic(bv.Expression.__lt__)

def test_le():
    binary_concrete_against_symbolic(bv.Expression.__le__)
    
def test_eq():
    binary_concrete_against_symbolic(bv.Expression.__eq__)

def test_ne():
    binary_concrete_against_symbolic(bv.Expression.__ne__)

def test_gt():
    binary_concrete_against_symbolic(bv.Expression.__gt__)

def test_ge():
    binary_concrete_against_symbolic(bv.Expression.__ge__)

def test_add():
    binary_concrete_against_symbolic(bv.Expression.__add__)
    
def test_sub():
    binary_concrete_against_symbolic(bv.Expression.__sub__)

def test_mul():
    binary_concrete_against_symbolic(bv.Expression.__mul__)
    
def test_floordiv():
    binary_concrete_against_symbolic_nozero(bv.Expression.__floordiv__)
    
def test_mod():
    binary_concrete_against_symbolic_nozero(bv.Expression.__mod__)

def test_lshift():
    # TODO: implement
    pass
    
def test_rshift():
    # TODO: implement
    pass

def test_and():
    binary_concrete_against_symbolic(bv.Expression.__and__)

def test_xor():
    binary_concrete_against_symbolic(bv.Expression.__xor__)
    
def test_or():
    binary_concrete_against_symbolic(bv.Expression.__or__)

def test_neg():
    unary_concrete_against_symbolic(bv.Expression.__neg__)

def test_invert():
    unary_concrete_against_symbolic(bv.Expression.__invert__)

if __name__ == '__main__':
    nose.main()
