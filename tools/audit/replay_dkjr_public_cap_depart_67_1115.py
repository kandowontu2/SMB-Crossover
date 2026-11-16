"""Depart after actual first pipe-cap support, preserving the low-wait negative."""
from hashlib import sha256
import replay_dkjr_public_low_depart_67_1115 as Prior

Old = Prior.Old
MARKER = '''   if player>=edge-1 and player<=edge+1 and carried(u,up)and grounded
     and up-32==y and descending and up>=154 and up<=160 then
    assert(cap-up<ram(2,0x7b),'First-pipe departure retains original safe fall distance')
'''
REPLACEMENT = '''   local onStaticCap=player>=pipe-2 and grounded and read(0x1e)==0
     and y==cap-32 and ram(2,0x210)==cap-17 and up>=cap+4
   local lowCarried=player>=edge-1 and player<=edge+1 and carried(u,up)and grounded
     and up-32==y and descending and up>=154 and up<=160
   if onStaticCap or lowCarried then
    assert(onStaticCap or cap-up<ram(2,0x7b),'First-pipe departure retains original safe fall distance')
'''


def controller(raw):
    text = Prior.controller(raw)
    assert sha256(text.encode()).hexdigest() == 'f3e772cb69a17803efb3b772f60d4806744c22fc90973309d50d011860f3dd8e'
    assert text.count(MARKER) == 1
    result = text.replace(MARKER, REPLACEMENT, 1)
    assert result.replace(REPLACEMENT, MARKER, 1) == text
    Prior.LuaRuntime().compile(result)
    return result
