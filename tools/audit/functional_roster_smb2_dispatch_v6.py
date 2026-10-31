"""Complete parent callbacks at their real caller return boundary.

V5 retained its preflight failure: it constructed but omitted applying the
literal helper replacement. Only the fixture gets a real completed-return
boundary; no product source, guards, imports or cart are changed.
"""
from pathlib import Path
import runpy
p=Path(__file__).with_name('functional_roster_smb2_dispatch_v3.py')
ns=runpy.run_path(str(p),run_name='prepare_only');g=ns['main'].__globals__;T=g['T'];B=g['B']
text=Path(T.__file__).read_text();src=text[text.index('def endpoint('):text.index('\ndef same(')]
anchor="if c.pc in[m.lab['FarCallCommon'],m.lab['FarCallCommon']+3]:maps+=1"
new="""if c.pc==0x7fff:
   return dict(dest=0x7fff,bank=m.tags[1],regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,mapper_entries=maps,minimumSP=low,completed=True),m,c
  """+anchor
assert src.count(anchor)==1
src=src.replace(anchor,new)
exec(compile(src,__file__,'exec'),T.__dict__)
assert 32767 in T.endpoint.__code__.co_consts
g['O']=B.O/'dispatch-controls-v6'
if __name__=='__main__':ns['main']()
