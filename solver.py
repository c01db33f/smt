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

"""smt.solver

Implements the actual 'using an SMT solver bit'. Backend has only
been tested with z3. Note that it will fill /tmp up with lots of
nonsense smt2 files.
"""

import os
import re
import subprocess
import time

import smt.bitvector as bv
import smt.boolean as bl
from smt.enums import *
from smt.utils import *


cache_hits = 0
cache_misses = 0


class Solver(object):
    
    bl_re = re.compile('''\(define-fun[\s\r\n]*([a-zA-Z0-9_]*)[\s\r\n]*\(\)[\s\r\n]*Bool[\s\r\n]*(true|false)[\s\r\n]*\)''')
    bv_re = re.compile('''\(define-fun[\s\r\n]*([a-zA-Z0-9_]*)[\s\r\n]*\(\)[\s\r\n]*\(_[\s\r\n]*BitVec[\s\r\n]*([0-9]*)\)[\s\r\n]*#x([0-9a-fA-F]*)[\s\r\n]*\)''')
    
    smt2_cache = {}
    symbol_cache = {}
        
    cache = dict()
    model_cache = dict()
    
    def __init__(self, parent=None):
        self._parent = parent
        self._roots = []
        self._solve_time = 0
        
    def fork(self):
        return Solver(self), Solver(self)

    def flatten(self):
        self._roots = self.roots()
        self._parent = None

    def concretise(self):
        m = self.model()
        self._roots = []
        for symbol_name in m:
            symbol_value = m[symbol_name]
            self.add(bv.Symbol(symbol_value.size, symbol_name) == symbol_value)

    def solve_time(self):
        return self._solve_time

    def add(self, expr):
        self._roots.append(expr)
        self._cache(expr)

    def roots(self):
        r = []
        s = self
        while s is not None:
            r += s._roots
            s = s._parent
        return r

    def _cache(self, expr):
        if expr not in self.smt2_cache:
            self.smt2_cache[expr] = expr.smt2()
        if expr not in self.symbol_cache:
            self.symbol_cache[expr] = expr.symbols()
        
    def _hash(self, expr=None):
        output = 0
        
        if expr:
            output = hash(expr)
        
        for root in self.roots():
            output += (101 * hash(root))
            output &= 0xffffffffffffffff
        
        return abs(output)

    def _smt2(self, expr=None):
        smt2 = ''
        
        expressions = self.roots()
        if expr is not None:
            self._cache(expr)
            expressions.append(expr)
    
        symbols = set()
        for e in expressions:
            symbols.update(e.symbols())
        
        for symbol in symbols:
            if isinstance(symbol, bl.Symbol):
                smt2 += '(declare-fun {0} () Bool)\n'.format(symbol.name) 
            elif isinstance(symbol, bv.Symbol):
                smt2 += '(declare-fun {0} () (_ BitVec {1}))\n'.format(symbol.name, symbol.size)
        
        for e in expressions:
            smt2 += '(assert {0})\n'.format(e.smt2())
        
        return smt2
    
    def _call_solver(self, smt2, in_file, out_file):
        try:
            # we use disk as a persistent second level cache...
            with open(out_file, 'r') as tmp:
                output = tmp.read()
                
            global cache_hits
            cache_hits += 1
            
        except:

            global cache_misses
            cache_misses += 1

            started = time.time()
            with open(in_file, 'w') as tmp:
                tmp.write(smt2)
            
            command = 'z3 -smt2 {0} > {1}'.format(in_file, out_file)
            subprocess.call(command, shell=True)

            with open(out_file, 'r') as tmp:
                output = tmp.read()

            finished = time.time()
            self._solve_time = finished - started

            os.unlink(in_file)
            #os.unlink(out_file)
            
        return output
        
    def _parse_model(self, results, expr=None):
        output = dict()
        
        expressions = list(self.roots())
        if expr is not None:
            self._cache(expr)
            expressions.append(expr)
    
        symbols = set()
        for e in expressions:

            symbols.update(e.symbols())
        
        for bl_match in self.bl_re.findall(results):
            name = bl_match[0]
            if bl_match[1] == 'true':
                value = True
            else:
                value = False
            output[name] = bl.Constant(value)
        
        for bv_match in self.bv_re.findall(results):
            name = bv_match[0]
            size = int(bv_match[1])
            value = int('0x' + bv_match[2], 16)
            output[name] = bv.Constant(size, value)
        
        for symbol in symbols:
            if symbol.name not in output:
                if isinstance(symbol, bv.Expression):
                    output[symbol.name] = bv.Constant(symbol.size, 0x2323232323232323)
                else:
                    output[symbol.name] = bl.Constant(True)
        
        return output
        
    def check(self, expr=None):
        if expr is not None and not expr.symbolic:
            return expr.value

        #print 'check {}'.format(expr.smt2())
        
        smt2 = '(set-logic QF_BV)\n'
        smt2 += self._smt2(expr)
        smt2 += '(check-sat)\n'
        
        smt2_hash = string_hash(smt2)
        if smt2_hash not in self.cache:
            in_file = '/tmp/{0:016x}.check.smt2'.format(smt2_hash)
            out_file = '/tmp/{0:016x}.check'.format(smt2_hash)
            results = self._call_solver(smt2, in_file, out_file)
            if results.startswith('sat'):
                self.cache[smt2_hash] = True
            elif results.startswith('unsat'):
                self.cache[smt2_hash] = False
            else:
                raise SolverError(results.splitlines()[0], smt2)
        else:
            global cache_hits
            cache_hits += 1
            
        return self.cache[smt2_hash]
        
    def model(self, expr=None):
        smt2 = '(set-logic QF_BV)\n'
        smt2 += self._smt2(expr)
        smt2 += '(check-sat)\n'
        smt2 += '(get-model)\n'
        
        smt2_hash = string_hash(smt2)
        if smt2_hash not in self.model_cache:
            in_file = '/tmp/{0:016x}.model.smt2'.format(smt2_hash)
            out_file = '/tmp/{0:016x}.model'.format(smt2_hash)
            results = self._call_solver(smt2, in_file, out_file)
            if results.startswith('sat'):
                self.model_cache[smt2_hash] = self._parse_model(results, expr)
            elif results.startswith('unsat'):
                self.model_cache[smt2_hash] = None
            else:
                raise SolverError(results.splitlines()[0], smt2)
        else:
            global cache_hits
            cache_hits += 1
        
        return self.model_cache[smt2_hash]