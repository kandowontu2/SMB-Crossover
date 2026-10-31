"""Exact bounded mask factor and original strict radius comparator controls."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
P=R/'build/contra-force-projectile-contact-1031-v3';O=R/'build/contra-force-projectile-mask-controls-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,mask_cases=0,axis_cases=0)
 try:
  A.K=P/'kernel';A.bind(P);V,Q,T,C,U=A.V,A.Q,A.T,A.C,A.U
  base=V.scene(0,shot=False,world=False);T.put(base,CurrentBank=3,CurrentBankC=2);base[0x5115]=3;base[0x5116]=2
  base.writes.clear();base.ram_writes.clear();base.ppu_log.clear();base.executed_guest.clear()
  old=(R/'build/contra-force-p1-kernel-v1/native-mask.s').read_text();values=[]
  for line in old.splitlines():
   if '.byte'in line:values.extend(int(v.strip().replace('$','0x'),0)for v in line.split('.byte')[1].split(','))
  assert len(values)==145 and values[:64]==[0]+[2]*63
  for y in range(145):
   for p in[v for v in range(256)if v&48==48]:
    m=C.clone(base);c=T.NesMPU(memory=m,pc=Q.L['CfNativeP1MaskRead']);c.a=71;c.x=43;c.y=y;c.p=p;c.sp=192;start=c.sp
    before=len(m.writes);steps=0;tail=False
    while c.pc!=Q.L['CfNativeP1MaskReadEnd']:
     assert steps<30
     if c.pc==Q.L['NativeMaskTail']:
      assert y>=64 and m[c.pc]==0xb9
      ptr=m[c.pc+1]+256*m[c.pc+2]+y
      assert ptr==Q.L['CfNativeP1MaskTail']+y-64;tail=True
     c.step();steps+=1
    wantp=(p&~130)|(2 if values[y]==0 else 0)
    assert(c.a,c.x,c.y,c.p,c.sp)==(values[y],43,y,wantp,start),(y,p,c.a,c.x,c.y,c.p)
    assert tail==(y>=64)and m.rawtags==base.rawtags and T.smc(m)==T.smc(base)
    w=[(a,v)for a,v in m.writes[before:]if not 0x100<=a<0x200]
    assert w==[(Q.L['CfState']+0x2f7,values[y])],(y,p,w)
    d['mask_cases']+=1
  d.update(passed=True,all145mask_IDs_64flags=True,full_AXYP_stack_maps_SMC_singlewrite_exact=True,scope='Same exact9280 bounded mask-source cases, rerun alone. Cold loader observer logs cleared before clone for speed only; no emulated state changed. No axis/native/earned-shot/readiness claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),Path(A.__file__),P/'source-stage.json',P/'kernel/runtime.lbl',P/'kernel/contact-runtime.s',P/'kernel/p1-runtime.s',R/'build/contra-force-p1-kernel-v1/native-mask.s']
  d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],mask=d['mask_cases'],axis=d['axis_cases'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
