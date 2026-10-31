"""Retain v3: a genuine direct Sunny callback returned normally at7FFF.

The endpoint helper previously demanded a second farcall and called its
own return sentinel a BRK. Complete direct callbacks now compare their
entire actual returned state/ABI as well; no source worker is bypassed.
"""
from pathlib import Path
import inspect
import current_quick_transport_controls_v4 as T
src=inspect.getsource(T.endpoint)
anchor="if c.pc in[m.lab['FarCallCommon'],m.lab['FarCallCommon']+3]:maps+=1"
new="""if c.pc==0x7fff:
   return dict(dest=0x7fff,bank=m.tags[1],regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,mapper_entries=maps,minimumSP=low,completed=True),m,c
  """+anchor
assert src.count(anchor)==1;exec(compile(src,__file__,'exec'),T.__dict__)
p=Path(__file__).with_name('functional_roster_smb2_dispatch_v3.py');text=p.read_text()
text=text.replace("B.O/'dispatch-controls-v3'","B.O/'dispatch-controls-v4'")
anchor="if not matched and (x['dest'],x['bank'])==(y['dest'],y['bank']):"
new="""if x.get('completed')or y.get('completed'):
  assert x.get('completed')and y.get('completed'),('complete source return boundary',case,x,y)
  matched=['complete-original-callback-return']
 if not matched and (x['dest'],x['bank'])==(y['dest'],y['bank']):"""
assert text.count(anchor)==1;text=text.replace(anchor,new)
exec(compile(text,__file__,'exec'),globals())
