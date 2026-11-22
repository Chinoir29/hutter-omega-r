"""Independent Python unlimited-int reimplementation of the Q32 Bayesian gate.

It is a numerical cross-check, not a compressor or a Hutter Prize score.
"""
from __future__ import annotations
UNIT=1<<32

def clamp(value:int)->int:
    return max(1,min(UNIT-1,value))

def reference_checksum(n:int=8192)->str:
    weights=[None]*256
    counts0=[0]*256
    counts1=[0]*256
    check=1469598103934665603
    state=0x9e3779b9
    for _ in range(n):
        state=(state*1664525+1013904223)&0xffffffff
        ctx=1+((state>>16)%255)
        base=1+(state%4294967294)
        bit=(state>>31)&1
        total=counts0[ctx]+counts1[ctx]
        weight=UNIT//2 if total==0 else weights[ctx]
        numer=(2*counts1[ctx]+1)*UNIT
        denom=2*(total+1)
        pkt=clamp((numer+denom//2)//denom)
        mix=clamp((weight*pkt+(UNIT-weight)*base+UNIT//2)//UNIT)
        check=((check^mix)*1099511628211)&0xffffffffffffffff
        lk_kt=pkt if bit else UNIT-pkt
        lk_base=base if bit else UNIT-base
        bayes_den=weight*lk_kt+(UNIT-weight)*lk_base
        assert bayes_den
        weights[ctx]=(weight*lk_kt*UNIT+bayes_den//2)//bayes_den
        if bit:counts1[ctx]+=1
        else:counts0[ctx]+=1
    return f'{check:016x}'

if __name__=='__main__':
    print('OMR28_Q32_CROSS_IMPL',reference_checksum())
