"""Finite real ISR cuts through the new exact inline native-mask factor."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
P=R/'build/contra-force-projectile-contact-1031-v3';O=R/'build/contra-force-projectile-mask-vectors-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,cuts=[])
 try:
  A.K=P/'kernel';A.bind(P);V,Q,T,C,U=A.V,A.Q,A.T,A.C,A.U
  base=V.scene(0,shot=False,world=False);T.put(base,CurrentBank=3,CurrentBankC=2,FamilyMainCommit=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,ReloadCHRBank=0,SavedJoypadBits=0,SavedJoypad1Bits=0)
  base[0x5115]=3;base[0x5116]=2;base[T.address(T.B,'VRAM_Buffer1')]=0;base[0x5224]=128
  base.writes.clear();base.ram_writes.clear();base.ppu_log.clear();base.executed_guest.clear()
  def start(m,y):
   c=T.NesMPU(memory=m,pc=Q.L['CfNativeP1MaskRead']);c.a=71;c.x=43;c.y=y;c.p=0x30;c.sp=192;return c
  def finish(m,c):
   for _ in range(30):
    if c.pc==Q.L['CfNativeP1MaskReadEnd']:return(c.a,c.x,c.y,c.p,c.sp)
    c.step()
   raise AssertionError('Mask micro timeout')
  for mode in ['normal','lag','paused-normal','paused-lag']:
   for y in [0,1,63,64,144]:
    m=C.clone(base);T.put(m,NmiDisable=0 if mode in('normal','paused-normal')else 255,GamePauseStatus=1 if mode.startswith('paused')else 0)
    ref=C.clone(m);expected=finish(ref,start(ref,y));c=start(m,y)
    while c.pc!=Q.L['CfNativeP1MaskReadEnd']:
     for kind in ['NMI','IRQ']:
      if kind=='IRQ'and c.p&4:continue
      z,zc=U.clone(m,c);proof=U.interrupt(z,zc,kind,keep_ppu=False);actual=finish(z,zc)
      assert actual==expected and z.rawtags==ref.rawtags and T.smc(z)==T.smc(ref)
      assert [bytes(b)for b in z.ram]==[bytes(b)for b in ref.ram]
      d['cuts'].append(dict(mode=mode,ID=y,kind=kind,PC=c.pc,SP=c.sp,**proof))
     c.step()
  d.update(passed=True,actual_cuts=len(d['cuts']),all_AXYP_SP_33SMC_maps_sourcepayload_exact=True,scope='Five actual bounded mask paths, normal/lag/paused native NMI and legal IRQ at every executed instruction. ISR effects retained. Internal source micro API after genuine loader; no native/cold/controller claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),Path(A.__file__),Path(A.U.__file__),P/'source-stage.json',P/'kernel/runtime.lbl'];d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],cuts=len(d['cuts']),error=d.get('error'))),flush=True)
if __name__=='__main__':main()
