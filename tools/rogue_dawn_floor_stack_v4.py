"""Changed floor/support branch action stack and all external fixup closure."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_floor_controls_v1 as base
import rogue_dawn_scheduler_controls_v3 as v
import rogue_dawn_scheduler_deep_edges_v1 as deep
q,put,address=v.q,v.put,v.address
O=R/'build/rogue-dawn-floor-v4';P=base.P

def main():
 assert not(O/'stack-layout-controls.json').exists()
 b=v.scoped_load(O/'candidate.nes');old=v.scoped_load(P/'candidate.nes');rows=[]
 for action,pad in itertools.product([0,1,2,3,4,6],[0,128]):
  def scene():
   m=base.ready(b);v.nmi(m)
   put(m,RdAction=action,RdHeld=pad,RdFresh=pad,RdClock=0,NmiDisable=255)
   if action==3:put(m,RdRadiusY=8,RdAnimFrame=27,RdAnimReset=22,RdAnimIndex=22)
   return m
  m=scene();plain=deep.execute(m,'RdControlStep',192);cut=min(plain['trace'],key=lambda a:a[2])
  m=scene();z=deep.execute(m,'RdControlStep',192,cut,IRQ=(address(b,'RdaReadRomValue'),97,cut[2]-29))
  assert z['minimum_SP']>=128,(action,pad,z['minimum_SP'])
  rows.append(dict(action=action,pad=pad,publicSP=192,cut=[hex(cut[0]),cut[1],cut[2]],minimum_SP=z['minimum_SP'],ISR=z['interrupt']))
 # Every changed byte outside A95 is one actual relocated target operand.
 # Farcall target immediates remain literalLDA/STA; the C94 bridge has its
 # originalJSR, now linked to the genuinely moved RdHostDispatch entry.
 reloc=[];covered=set();a,z=old['raw'],b['raw']
 smc=address(b,'FarcallJmpTarget_SMC')
 for at in range(16,len(a)-10):
  bank=(at-16)//8192
  if bank==95:continue
  if a[at]==z[at]==0xa9 and a[at+2:at+6]==z[at+2:at+6]==bytes([0x8d,(smc+1)&255,(smc+1)>>8,0xa9]) and a[at+7:at+10]==z[at+7:at+10]==bytes([0x8d,(smc+2)&255,(smc+2)>>8]):
   before=a[at+1]+256*a[at+6];after=z[at+1]+256*z[at+6]
   if before!=after:
    assert after==before+17 and 0xa600<=before<0xbf00,(bank,hex(before),hex(after))
    covered.update([at+1,at+6]);reloc.append(dict(bank=bank,offset=hex((at-16)%8192),before=hex(before),after=hex(after),kind='genuine18Bfarcall target'))
  if bank==94 and a[at]==z[at]==0x20:
   before=int.from_bytes(a[at+1:at+3],'little');after=int.from_bytes(z[at+1:at+3],'little')
   if before!=after and before==address(old,'RdHostDispatch'):
    assert after==address(b,'RdHostDispatch')==before+17
    covered.update([at+1,at+2]);reloc.append(dict(bank=bank,offset=hex((at-16)%8192),before=hex(before),after=hex(after),kind='originalC94bridge JSR genuineowner'))
 outside=[i for i,(x,y)in enumerate(zip(a,z))if x!=y and(i-16)//8192!=95]
 assert set(outside)<=covered,[hex(i)for i in outside if i not in covered]
 assert a[16+95*8192+0x1f00:16+95*8192+0x1f32]==z[16+95*8192+0x1f00:16+95*8192+0x1f32]
 out=dict(passed=True,source_CPU_only=True,native_run=False,source_action_stack_cases=rows,
  minimum_SP=min(r['minimum_SP']for r in rows),all_outside_A95_diff_bytes=len(outside),actual_relocations=reloc,
  limits=['Finite genuineCPU Control192 plus full actual lagNMI and trueIRQ; no nativePPU/FPS/audio claim.',
          'NormalNMI runs outside admittedMain; Main has actualNmiDisableFF. Frozen regularNMI closure is reused for unchanged audio/scheduler.',
          'C94bridge source/PC/ABI remain unchanged, one genuineJSR operand follows its real A95target. No fakeDBG aliases.'],
  bindings=[v.ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',R/'tools/rogue_dawn_scheduler_deep_edges_v1.py']])
 (O/'stack-layout-controls.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(passed=True,cases=len(rows),minimum_SP=out['minimum_SP'],relocated_operands=len(reloc),outside_bytes=len(outside))))
if __name__=='__main__':main()
