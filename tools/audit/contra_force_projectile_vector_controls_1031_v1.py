"""Real native ISR cuts in the new CF contact phase and exact mask lookup."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
P=R/'build/contra-force-projectile-contact-1031-v3';O=R/'build/contra-force-projectile-vector-controls-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,cuts=[])
 try:
  A.K=P/'kernel';A.bind(P);V,Q,T,C,U=A.V,A.Q,A.T,A.C,A.U
  for cls in range(4):
   base=V.scene(cls,shot=False,world=False)
   T.put(base,CurrentBank=3,CurrentBankC=2,FamilyMainCommit=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,ReloadCHRBank=0,SavedJoypadBits=0,SavedJoypad1Bits=0)
   base[0x5115]=3;base[0x5116]=2;base[T.address(T.B,'VRAM_Buffer1')]=0;base[0x5224]=128
   for i in range(6):base[T.address(T.B,'Enemy_Flag')+i]=0
   T.put(base,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_Y_HighPos=1,Enemy_X_Position=160,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_BoundBoxCtrl=9,ObjectOffset=5,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
   for off,val in [(0x382+10,1),(0x334+10,28),(0x31a+10,5),(0x420+10,6),(0x34e+10,160),(0x368+10,193),(0x39c+10,144),(0x3b2+10,11),(0x2fc,10),(0x53,10),(0x36,13)]:base.ram[2][off]=val
   for mode in ['normal','lag','paused-normal','paused-lag']:
    m=C.clone(base);T.put(m,NmiDisable=0 if mode in('normal','paused-normal')else 255,GamePauseStatus=1 if mode.startswith('paused')else 0)
    m.writes.clear();m.ram_writes.clear();m.ppu_log.clear();m.executed_guest.clear()
    ref=C.clone(m);expected=T.finish(ref,C.start(ref,Q.L['CfHostShotContacts'],3,a=87,x=10,y=3,p=0x30))
    assert T.get(ref,'Enemy_State')&32 and T.get(ref,'ObjectOffset')==5
    c=C.start(m,Q.L['CfHostShotContacts'],3,a=87,x=10,y=3,p=0x30);seen=set()
    while c.pc!=0x7fff:
     raw=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
     own=raw==1 and Q.L['CfContactAxis']<=c.pc<Q.L['CfContactAxisEnd']
     gate=raw==2 and Q.L['CfContactAxisGate']<=c.pc<Q.L['CfNativeTargetTop']
     phase=raw==2 and Q.L['CfCallA']<=c.pc<Q.L['CfCallA']+55
     key=(raw,c.pc,T.get(m,'R4'))
     if(own or gate or phase)and key not in seen:
      seen.add(key)
      for kind in ['NMI','IRQ']:
       if kind=='IRQ'and c.p&4:continue
       z,zCPU=U.clone(m,c);before=A.raw_global(z);proof=U.interrupt(z,zCPU,kind,keep_ppu=False);after=A.raw_global(z)
       effects=[a for a,(x,y)in enumerate(zip(before,after))if x!=y];actual=T.finish(z,zCPU)
       assert actual['AXYP']==expected['AXYP']and z.rawtags==ref.rawtags and T.smc(z)==T.smc(ref)
       assert[bytes(b)for b in z.ram]==[bytes(b)for b in ref.ram]
       wanted=A.raw_global(ref)
       for at in effects:wanted[at]=after[at]
       diff=[a for a in range(32768)if not 0x100<=a<=0x1e0 and list.__getitem__(z,a)!=wanted[a]]
       assert not diff,(cls,mode,kind,key,diff)
       d['cuts'].append(dict(variant=cls,mode=mode,raw=raw,PC=c.pc,radius=key[2],entry_SP=c.sp,ISR_effects=effects,**proof))
     c.step()
    assert any(raw==1 for raw,pc,r in seen)and any(raw==2 for raw,pc,r in seen)
  d.update(passed=True,actual_cuts=len(d['cuts']),full_AXYP_livepage1_33SMC_maps_source_state=True,scope='Genuine-loader authenticated explicit healthy Goomba+legal pistol geometry fixture. Actual outerSFCâ†’A3â†’C2â†’A1 phase target and source impact. Native normal/lag/pausedNMI+legalIRQ executed, all ISR effects retained. Not native/controller/cold-earned proof.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),Path(A.__file__),Path(A.U.__file__),P/'source-stage.json',P/'kernel/runtime.lbl'];d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],cuts=len(d['cuts']),error=d.get('error'))),flush=True)
if __name__=='__main__':main()
