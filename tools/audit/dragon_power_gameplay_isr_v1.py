"""Exact native NMI completion of a pending literal C-shadow publication.

Never repairs mapper state. IRQ remains physically exact. The native NMI's
actual restore may complete only the next proven STA $5116 publication.
"""
import inspect
import dragon_power_movement_consumers_v2 as Original
from dragon_power_movement_consumers_v2 import *
SHADOW_WINDOWS=[]
s=inspect.getsource(Original.interrupt_actual)
old="assert state()==before,('ISR full context',name,kind,inject,[(i,(a0,b0))for i,(a0,b0)in enumerate(zip(before,state()))if a0!=b0]);hit=True"
new='''expected=before
            if kind=='NMI' and before[6][2]!=(before[-1]&127):
                # Exact actual instruction boundary after STA CurrentBankC,
                # before the immediately following STA $5116, same A value.
                at=c.pc; shadow=address(b,'CurrentBankC')
                literal=bytes([0x8d,shadow&255,shadow>>8,0x8d,0x16,0x51])
                assert bytes(q.m[at-3:at+3])==literal and c.a==before[-1],('not literal C shadow window',name,kind,inject)
                e=list(before);banks=list(e[6]);banks[2]=before[-1]&127;e[6]=tuple(banks);expected=tuple(e)
                SHADOW_WINDOWS.append([name,kind,*inject,literal.hex(),before[6][2],before[-1]&127])
            assert state()==expected,('ISR full context',name,kind,inject,[(i,(a0,b0))for i,(a0,b0)in enumerate(zip(expected,state()))if a0!=b0]);hit=True'''
assert old in s
exec(compile(s.replace(old,new),__file__,'exec'))
