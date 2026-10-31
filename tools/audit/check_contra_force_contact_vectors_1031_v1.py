"""Narrow genuine public0 cuts around the CF world/previous-contact repair."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
O=R/'build/contra-force-contact-vector-controls-1031-v1'
P=R/'build/contra-force-world-roles-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,source_CPU=True,native=False,checks=[])
 try:
  A.bind(P);V,Q,T,C,U=A.V,A.Q,A.T,A.C,A.U
  points={Q.L['CfHostMovement']+3,Q.L['CfHostAfterBG'],Q.L['CfHostAfterBG']+3,Q.L['CfHostScript']}
  for cls in range(4):
   m=V.scene(cls,shot=False,world=False)
   T.put(m,OperMode=1,OperMode_Task=1,Player_X_Position=96,Player_Y_Position=88,Player_Y_HighPos=1,
         CurrentOAMOffset=0,RgOamRotation=0,GuestOamRotationActive=0,FamilyMainCommit=1,NmiDisable=255,
         ReloadCHRBank=0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0)
   m[T.address(T.B,'VRAM_Buffer1')]=0;m[0x5224]=128
   T.put(m,OperMode_Task=3,GameEngineSubroutine=8,Player_Y_Position=176,SavedJoypadBits=128)
   ref=C.clone(m);expected=Q.public(ref,0,p=0x30)
   assert T.get(ref,'Player_Y_Position')<176
   # Genuine public arithmetic target, never a direct A3 entry/preload.
   c=Q.J.shared(m,0,p=0x30)
   seen=set()
   while c.pc!=0x7fff:
    if m.rawtags[1]==3 and c.pc in points and c.pc not in seen:
     seen.add(c.pc)
     for kind in('NMI','IRQ'):
      if kind=='IRQ'and c.p&4:continue
      z,d=U.clone(m,c);before=A.raw_global(z);proof=U.interrupt(z,d,kind,keep_ppu=False)
      after=A.raw_global(z);effects=[i for i,(a,b)in enumerate(zip(before,after))if a!=b]
      actual=T.finish(z,d)
      assert actual['AXYP']==expected['AXYP']and z.rawtags==ref.rawtags and T.smc(z)==T.smc(ref)
      assert [bytes(b)for b in z.ram]==[bytes(b)for b in ref.ram]
      wanted=A.raw_global(ref)
      for at in effects:wanted[at]=after[at]
      differences=[at for at in range(32768)if not 0x100<=at<=0x1e0 and list.__getitem__(z,at)!=wanted[at]]
      assert not differences,(cls,kind,hex(c.pc),differences)
      assert T.get(z,'Player_Y_Position')==T.get(ref,'Player_Y_Position')
      out['checks'].append(dict(variant=cls,PC=c.pc,SP=c.sp,native_ISR_effects=effects,**proof))
    c.step()
   assert seen==points,(cls,points-seen)
  out.update(passed=True,cuts=len(out['checks']),classes=4,full_AXYP_page1_33SMC_maps_restored=True)
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  out['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg']}
  path=O/'controls.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(path),passed=out['passed'],sha256=sha(path),error=out.get('error'),cuts=out.get('cuts'))),flush=True)
if __name__=='__main__':main()
