#!/usr/bin/env python3
"""OMÉGA-R v0.33 — reversible line/template LAB; no Hutter Prize score.
Escape grammar: 0x1b 0x1b for literal ESC, 0x1b 0x00 plus varint age
for an exact previous line, 0x1b 0x01 plus varint age then numeric
tokens for the next line's digit slots. Strictly LF-delimited.
No external dictionary, bytes or trained model needed by the decoder.
Copyright (c) 2026 OMÉGA-R, SPDX-License-Identifier: MIT.
"""
import argparse
import hashlib
import json
import re
from collections import deque
from pathlib import Path

MAGIC = b'OMR33LT1\x00'
ESC = 27
RX = re.compile(rb'[0-9]+')

def vint(v):
    if not 0 <= v < 2**64: raise ValueError('varint out of range')
    b = bytearray()
    while v > 127:
        b.append((v & 127) | 128)
        v >>= 7
    b.append(v)
    return bytes(b)

def read_vint(b, p):
    value=0
    for i in range(10):
        if p >= len(b): raise ValueError('truncated varint')
        x=b[p]; p+=1
        if i==9 and x>1: raise ValueError('overflow')
        value |= (x & 127) << (i*7)
        if x<128:
            if i and x==0: raise ValueError('noncanonical varint')
            return value,p
    raise ValueError('overflow')

def skeleton(line):
    return tuple(RX.split(line)), tuple(RX.findall(line))

class Dictionary:
    def __init__(self,window,min_len,max_len):
        if not 1 <= window <= 65536 or min_len<1 or max_len<min_len:
            raise ValueError('invalid dictionary parameters')
        self.window=window
        self.min_len=min_len
        self.max_len=max_len
        self.lines=deque(maxlen=window)
        self.count=0
        self.exact={}
        self.pattern={}
    def insert(self,line):
        if line.endswith(b'\n') and self.min_len<=len(line)<=self.max_len:
            self.exact[line]=self.count
            k, nums=skeleton(line)
            if nums: self.pattern[k]=self.count
        self.lines.append(line)
        self.count+=1
    def previous(self,idx):
        age=self.count-1-idx
        if not 0<=age<len(self.lines):
            raise ValueError('reference outside history window')
        return age,self.lines[-age-1]
    def find(self,idx):
        if idx is None: return None
        try: return self.previous(idx)
        except ValueError: return None

def source_lines(src):
    parts=src.split(b'\n')
    for n,p in enumerate(parts):
        if n==len(parts)-1 and not p: continue
        yield p+(b'\n' if n<len(parts)-1 else b'')

def encode(raw, mode='hybrid',window=8192,min_len=32,max_len=16384):
    if mode not in ('literal','exact','template','hybrid'): raise ValueError('mode')
    db=Dictionary(window,min_len,max_len)
    output=bytearray(MAGIC+vint(window)+vint(min_len)+vint(max_len))
    count={'literal':0,'exact':0,'template':0}
    for line in source_lines(raw):
        command=None
        if line.endswith(b'\n') and min_len<=len(line)<=max_len:
            if mode in ('exact','hybrid'):
                c=db.find(db.exact.get(line))
                if c: command=b'\x1b\x00'+vint(c[0])
            if command is None and mode in ('template','hybrid'):
                key, nums=skeleton(line)
                if nums:
                    c=db.find(db.pattern.get(key))
                    if c:
                        prev_key,prev_nums=skeleton(c[1])
                        assert prev_key==key and len(prev_nums)==len(nums)
                        tmp=b'\x1b\x01'+vint(c[0])+b''.join(vint(len(v))+v for v in nums)
                        if len(tmp)<len(line)+line.count(ESC): command=tmp
        if command is None:
            output+=line.replace(b'\x1b',b'\x1b\x1b')
            count['literal']+=1
        else:
            output+=command
            count['exact' if command[1]==0 else 'template']+=1
        db.insert(line)
    return bytes(output),count

def decode(data):
    if not data.startswith(MAGIC): raise ValueError('bad magic')
    p=len(MAGIC)
    window,p=read_vint(data,p)
    min_len,p=read_vint(data,p)
    max_len,p=read_vint(data,p)
    db=Dictionary(window,min_len,max_len)
    out=bytearray(); line=bytearray()
    while p<len(data):
        x=data[p]; p+=1
        if x==ESC:
            if p>=len(data): raise ValueError('truncated escape')
            op=data[p]; p+=1
            if op==ESC: x=ESC
            elif op in (0,1):
                if line: raise ValueError('reference not at line start')
                age,p=read_vint(data,p)
                _,prev=db.previous(db.count-1-age)
                if not prev.endswith(b'\n'):raise ValueError('bad base line')
                if op==0: expanded=prev
                else:
                    parts,old_nums=skeleton(prev)
                    if not old_nums: raise ValueError('no numeric slots')
                    nums=[]
                    for _ in old_nums:
                        n,p=read_vint(data,p)
                        if n<1 or n>max_len or p+n>len(data): raise ValueError('bad numeric size')
                        digits=data[p:p+n]; p+=n
                        if not all(48<=v<=57 for v in digits):raise ValueError('bad digits')
                        nums.append(digits)
                    expanded=b''.join(s+(nums[i] if i<len(nums) else b'') for i,s in enumerate(parts))
                    if len(expanded)>max_len: raise ValueError('line expansion overflow')
                out+=expanded
                db.insert(expanded)
                continue
            else: raise ValueError('unknown escape opcode')
        out.append(x)
        line.append(x)
        if x==10:
            db.insert(bytes(line));line.clear()
    if line: db.insert(bytes(line))
    return bytes(out)

def self_test():
    from random import Random
    rng=Random(330033)
    tests=[b'',b'\n',b'\r\n',bytes(range(256))*8,b'\x1b'*100,
           b'| Year 2005 Population 14 inhabitants total\n'*20+
           b'| Year 2019 Population 304 inhabitants total\n'*20]
    for _ in range(200):
        data=b''.join(rng.choice(tests)+rng.randbytes(rng.randrange(200)) for _ in range(5))
        tests.append(data)
        for mode in ('literal','exact','template','hybrid'):
            c,_=encode(data,mode=mode,window=64)
            assert decode(c)==data
    print('SELFTEST_OK',len(tests), 'families')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['encode','decode','test'])
    ap.add_argument('source',nargs='?',type=Path)
    ap.add_argument('destination',nargs='?',type=Path)
    ap.add_argument('--mode',default='hybrid',choices=['literal','exact','template','hybrid'])
    args=ap.parse_args()
    if args.action=='test':
        self_test()
        return
    if args.source is None or args.destination is None: ap.error('source and destination required')
    data=args.source.read_bytes()
    if args.action=='encode':
        result,counters=encode(data,args.mode)
        print(json.dumps({'size':len(result),'counters':counters}))
    else:
        result=decode(data)
        print(json.dumps({'size':len(result),'sha256':hashlib.sha256(result).hexdigest()}))
    args.destination.write_bytes(result)

if __name__=='__main__':main()
