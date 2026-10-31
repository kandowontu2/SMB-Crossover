"""Paired exact CF graphics ABI and real ISR cuts at the changed source seam."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_p1_coherent_controls_v2 as A
P=R/'build/contra-force-scroll-publisher-1031-v2';OLD=R/'build/contra-force-world-roles-1031-v2'
O=R/'build/contra-force-scroll-seam-controls-1031-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,source_CPU=True,native=False,pairs=[],vectors=[])
 try:
  A.K=OLD/'kernel';A.bind(OLD);V,Q,T,C,U=A.V,A.Q,A.T,A.C,A.U
  oldbases=[V.scene(v,shot=False,world=False)for v in range(4)]
  A.K=P/'kernel';A.bind(P);newbases=[V.scene(v,shot=False,world=False)for v in range(4)]
  pos=T.address(T.B,'Player_Pos_ForScroll');rel=T.address(T.B,'Player_Rel_XPos')
  for cls in range(4):
   for service in(1,3):
    for flags in[v for v in range(256)if v&48==48]:
     old,new=C.clone(oldbases[cls]),C.clone(newbases[cls])
     for m in(old,new):T.put(m,Player_Pos_ForScroll=0,Player_Rel_XPos=37)
     oldram=[bytes(x)for x in old.ram];newram=[bytes(x)for x in new.ram]
     a=Q.public(old,service,p=flags);z=Q.public(new,service,p=flags)
     assert a['AXYP']==z['AXYP']and old.rawtags==new.rawtags and T.smc(old)==T.smc(new)
     diff=[i for i in range(32768)if list.__getitem__(old,i)!=list.__getitem__(new,i)and not 0x100<=i<=0x1e0]
     assert diff==[pos]and old[pos]==0 and new[pos]==37,(cls,service,flags,diff)
     for bank in(0,1,2,3):
      # Compare actual state changes; code/cookie fingerprint differences are immutable inputs.
      da=[(i,x,y)for i,(x,y)in enumerate(zip(oldram[bank],bytes(old.ram[bank])))if x!=y]
      dz=[(i,x,y)for i,(x,y)in enumerate(zip(newram[bank],bytes(new.ram[bank])))if x!=y]
      assert da==dz,(cls,service,flags,bank,da,dz)
     assert z['CPU']-a['CPU']==24
     out['pairs'].append(dict(variant=cls,service=service,P=flags,AXYP=z['AXYP'],extraCPU=24))
  targets={Q.L['CfHostGraphics'],Q.L['CfHostGraphics']+3,Q.L['CfHostGraphics']+4,Q.L['CfHostEmptyPointer']}
  for pc in range(Q.L['CfHostScrollPublish'],Q.L['CfHostScrollPublishEnd']):
   # Every genuine helper instruction, not arbitrary operand-byte entry.
   pass
  targets|={Q.L['CfHostScrollPublish']+i for i in(0,3,6,8,11)}
  for cls in range(4):
   for mode in('normal','lag','paused'):
    m=C.clone(newbases[cls]);T.put(m,Player_Pos_ForScroll=0,Player_Rel_XPos=37,ReloadCHRBank=0,
      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,
      NmiDisable=0 if mode=='normal'else 255,GamePauseStatus=1 if mode=='paused'else 0)
    m[T.address(T.B,'VRAM_Buffer1')]=0;m[0x5224]=128
    ref=C.clone(m);expected=Q.public(ref,1,p=0x30)
    c=Q.J.shared(m,1,p=0x30);seen=set()
    while c.pc!=0x7fff:
     if m.rawtags[1]==3 and c.pc in targets and c.pc not in seen:
      seen.add(c.pc)
      for kind in('NMI','IRQ'):
       if kind=='IRQ'and c.p&4:continue
       z,d=U.clone(m,c);before=A.raw_global(z);proof=U.interrupt(z,d,kind,keep_ppu=False);after=A.raw_global(z)
       effects=[i for i,(x,y)in enumerate(zip(before,after))if x!=y]
       actual=T.finish(z,d)
       assert actual['AXYP']==expected['AXYP']and z.rawtags==ref.rawtags and T.smc(z)==T.smc(ref)
       assert[bytes(b)for b in z.ram]==[bytes(b)for b in ref.ram]
       wanted=A.raw_global(ref)
       for at in effects:wanted[at]=after[at]
       diffs=[at for at in range(32768)if not 0x100<=at<=0x1e0 and list.__getitem__(z,at)!=wanted[at]]
       assert not diffs,(cls,mode,kind,hex(c.pc),diffs)
       assert z[pos]==37 and z[rel]==37
       out['vectors'].append(dict(variant=cls,mode=mode,PC=c.pc,SP=c.sp,native_ISR_effects=effects,**proof))
     c.step()
    assert seen==targets,(cls,mode,targets-seen)
  out.update(passed=True,all64flags_graphics_pairs=len(out['pairs']),actual_native_ISR_cuts=len(out['vectors']),
    full_AXYP_live_page1_33SMC_rawmaps=True,scope='Isolated real ROM-guarded public graphics1/3 calls with actual forcedblank loader setup; explicit leaf relX37 input, no cold/fullroute claim. Native normal/lag/paused NMI and IRQ actual instructions; observed ISR writes are recorded, not source state normalization.')
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  out['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'kernel/runtime.lbl',OLD/'source-stage.json']}
  p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),passed=out['passed'],sha256=sha(p),error=out.get('error'),pairs=len(out['pairs']),cuts=len(out['vectors']))),flush=True)
if __name__=='__main__':main()
