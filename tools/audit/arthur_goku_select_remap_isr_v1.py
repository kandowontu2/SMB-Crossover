"""Real normal/lag NMI/IRQ cuts at new menu helpers and coordinate seams."""
from pathlib import Path
import json,traceback
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_visuals58_v1 as B
R=B.R;J=R/'build/arthur-goku-select-remap-v3/joint';O=J.parent;T=A.T;S=A.S;C=T.C

def main():
 out=O/'isr-controls.json';assert not out.exists();d=dict(passed=False,native=False);rows=[]
 try:
  base=T.bus(J)
  for n,v in [('OperMode',0),('CrossoverMenuState',2),('FamilyMainCommit',1),('GuestAudioCharacter',0),('GamePauseStatus',0),('SelectedCharacter',32),('FmAlts',128)]:base.set(n,v)
  # Direct true SFC entry is the same caller frame used by the genuine
  # native menu. Full caller/Start/Fresh semantics are in the menu receipt.
  for target,x,a in [('NrMenuCharacter',31,0x83),('NrMenuCharacter',9,0x83),('FmStartFlags',31,0x83),('FmStartFlags',9,0x83),('FmDrawPreviewSelected',0x5a,30),('FmDrawPreviewSelected',0x5a,32)]:
   m=T.fork(base);cuts=[];seen=set();age=0
   lo=m.lab['NrMenuAltTail'];start=m.lab['FmStartFlags'];draw=m.lab['FmDrawPreviewSelected'];end=m.lab['FmNames']
   def watch(c):
    nonlocal age
    tag=m.tags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
    key=(tag,c.pc);op=bytes(m[c.pc:c.pc+3])
    owned=(tag==252 and lo<=c.pc<lo+17)or(tag==204 and(start<=c.pc<start+28 or draw<=c.pc<end))
    if key not in seen and(owned or 0x15a<=c.pc<0x17b or op in[b'\x8d\x15\x51',b'\x8d\x16\x51']):seen.add(key);cuts.append((age,c.pc))
    age+=1
   reference=S.execute(m,target,A=a,X=x,Y=0xc7,P=0x71,hook=watch)[0]
   for at,pc in cuts:
    for lag in[0,255]:
     for kind in['NMI','IRQ']:
      q=T.fork(base);q.set('NmiDisable',lag);tick=0;proof=[]
      def inject(c):
       nonlocal tick
       if tick==at:
        assert c.pc==pc
        if kind!='IRQ'or not c.p&c.INTERRUPT:proof.append(C.interrupt_at(q,c,kind))
       tick+=1
      actual=S.execute(q,target,A=a,X=x,Y=0xc7,P=0x71,hook=inject)[0]
      assert actual==reference,('foreground AXYP/SP',target,x,a,at,kind,lag,reference,actual)
      if proof:rows.append(dict(target=target,X=x,A=a,step=at,PC=pc,lag=lag,**proof[0]))
  d.update(passed=True,real_vector_cuts=len(rows),rows=rows,scope='All reached helper/coordinate instructions plus real SMC and mapper seams, normal/lag NMI and unmasked IRQ. Actual context checker preserves all33SMC/liveAXYP/SP/staticpage1/maps/WRAM; no native or activeSMB2palette claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc(),completed_vectors=len(rows))
 d['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',O/'source-stage.json',Path(C.__file__)]}
 B.write(out,json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in['rows','bindings','traceback']}));assert d['passed'],d.get('error')

if __name__=='__main__':main()
