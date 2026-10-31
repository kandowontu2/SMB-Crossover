"""Retain true KmCycleEnd boundary; append only after its last source RTS.

v1 stopped before copying or compilation because the tail has an unreferenced
end marker. That marker is not payload; later include order appends Kama's
cycle after new_roster_dispatch.s, so the actual tail belongs after it.
"""
from pathlib import Path
p=Path(__file__).with_name('prepare_arthur_goku_select_remap_v1.py');s=p.read_text()
s=s.replace("O=R/'build/arthur-goku-select-remap-v1'","O=R/'build/arthur-goku-select-remap-v2'")
s=s.replace("assert not[n for n,s in old['syms'].items()if s.get('seg')==nrseg['id']and 0xadee<=int(s.get('val','0'),0)<0xae00]","""tail_symbols=[(n,z)for n,z in old['syms'].items()if z.get('seg')==nrseg['id']and 0xadee<=int(z.get('val','0'),0)<0xae00]
 assert len(tail_symbols)==1 and tail_symbols[0][0]=='KmCycleEnd'and 'ref'not in tail_symbols[0][1],tail_symbols""")
a=" t=once(t,end,'''";b=" edit(p,t)\n p=J/'src/kamikaze_mario.s';t=B.read(p);end='KmCycleEnd:\\n.assert * <= $ae00,lderror,\"Kamikaze cycle overlaps Rogue auxiliary\"'\n t=once(t,end,'''KmCycleEnd:\n"
assert s.count(a)==1;s=s.replace(a,b)
exec(compile(s,__file__,'exec'),globals())
