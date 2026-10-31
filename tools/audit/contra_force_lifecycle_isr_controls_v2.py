"""Narrow actual joined B020 saved frames/guard/familytail/A2 vector seams."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_loader_isr_controls_v2 as U
import contra_force_lifecycle_controls_v4 as Q
J,C,T=Q.J,Q.C,Q.T;U.B=T.B
O=R/'build/contra-force-lifecycle-isr-controls-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,actual_natural_cold_hook=False,checks={})
 try:
  rows=[];states=[]
  native_names=['BtRouter','BwBtResolve','BwResolveRAM','BwResolveRAMFinish','BwResolveFamilyTail','CfOrBtCheck','CfExternalCheck','CfExternalSet']
  native={T.address(T.B,n):n for n in native_names}
  own_names=['CfA2Router','CfA2Return','CfCallA','CfHostConstruct','CfHostSceneEnsure','CfHostEnsure','CfHostReset','CfHostAreaReset']
  own={Q.L[n]:n for n in own_names}
  bases=[Q.load(0)]
  for service,(lag,pause)in itertools.product([15,19],[(0,0),(0,1),(255,0)]):
   base=C.clone(bases[0]);Q.context(base);Q.public(base,15);T.put(base,SavedJoypadBits=(1 if lag else 0),NmiDisable=lag,GamePauseStatus=pause,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,Sprite0HitDetectFlag=0,ReloadCHRBank=0)
   base[T.address(T.B,'VRAM_Buffer1')]=0
   if service==15 and lag==0:T.put(base,OperMode=0) # Stable title rejection, not a guard made eligible by normalNMI decrement0toFF.
   expected=C.clone(base);e=J.shared(expected,service,p=0x31);T.finish(expected,e);wanted=[bytes(x)for x in expected.ram]
   m=C.clone(base);c=J.shared(m,service,p=0x31);seen=set();low=c.sp;steps=0
   while c.pc!=0x7fff:
    assert steps<100000
    pc=c.pc;raw=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    phy=(raw&127)if raw>=128 else(-2-raw if raw>=0 else-1)
    op=bytes(m[pc:pc+3]);label=native.get(pc)if raw>=128 else own.get(pc)
    # Exact entry plus both sides of real mapper stores/return boundaries;
    # full cookie loop replays are unnecessary for this outer-depth proof.
    reason=label
    if pc==T.address(T.B,'BtServiceVeneers')+3*service and raw==0xd7:reason='actual public rowJSR'
    if pc==Q.L['CfServiceVeneers']+3*service and raw==2:reason='first authenticated A2 opcode'
    if op in[b'\x8d\x15\x51',b'\x8d\x16\x51']:reason='actual mapper store'
    if (phy in[67,69,87]or raw==3)and m[pc]in[0x28,0x60]:reason='actual frame/return seam'
    if pc<0x8000 and m[pc]in[0x48,0x68,0x60]:reason='genuine SFC stack seam'
    key=(raw,pc)
    if reason and key not in seen:
     seen.add(key)
     for kind in['NMI','IRQ']:
      if kind=='IRQ'and c.p&4:continue
      z,d=U.clone(m,c);z[0x5204]=0x80;proof=U.interrupt(z,d,kind,keep_ppu=False);finish=T.finish(z,d)
      witness=dict(service=service,lag=lag,pause=pause,reason=reason,PC=pc,raw=raw,source_SP=c.sp,kind=kind,actual_AXYP=finish['AXYP'],expected_AXYP=[e.a,e.x,e.y,e.p],actual_rawtags=z.rawtags,expected_rawtags=base.rawtags)
      if finish['AXYP']!=[e.a,e.x,e.y,e.p]or z.rawtags!=base.rawtags:out['first_wrong']=witness;raise AssertionError(('joined continuation',witness))
      assert [bytes(x)for x in z.ram]==wanted,('postISR source continuation changed',service,lag,pause,pc,kind)
      rows.append(dict(service=service,lag=lag,pause=pause,reason=reason,PC=pc,raw=raw,source_SP=c.sp,**proof))
    low=min(low,c.sp);c.step();steps+=1
   assert [bytes(x)for x in m.ram]==wanted
   states.append(dict(service=service,lag=lag,pause=pause,min_foreground_SP=low,unique_joined_seams=len(seen)))
  assert any(r['reason']=='first authenticated A2 opcode'for r in rows)
  assert any(r['reason']=='BwResolveFamilyTail'for r in rows)
  out['checks']=dict(real_vector_cases=len(rows),actual_source_continuation_exact=True,normal_lag_paused_NMI_legalIRQ=True,actual_joined_frames_33SMC_page1_R0to7_and_rawmaps_preserved=True,foreground_states=states,rows=rows)
  out['retained_v1_negative']='V1 seeded an invalid NmiDisable0 scene while all OTHER accepted forcedblank conditions held. Actual normalNMI legitimately decrements0toFF, making later SceneEnsure eligible and C1. V2 normal15 cohorts use genuine stable title OperMode0; accepted forcedblank15 gets actual lagNMI/IRQ only. No product fix or state normalization.'
  out['scene_context']='Accepted SceneEnsure receives only real lag NMI/IRQ because NmiDisable<0 is its required forcedblank context; normal/paused15 cohorts reject without own state. Reset19 uses general Ensure and is tested normal/paused/lag.'
  out['controller_cohorts']='Normal/paused NMI uses stable zero native input, matching actual zero physical joypad; lag NMI retains held Right1. V1/V2 changed-input counterexample and exact native producer witness are preserved, not relabeled. Source continuation equivalence only claimed for these actual stable input cohorts.'
  out['passed']=True
 except Exception as e:out.update(failure=repr(e),traceback=traceback.format_exc());raise
 finally:
  paths=[Path(__file__),Path(J.__file__),Path(C.__file__),Path(T.__file__),Path(U.__file__),J.P/'source-stage.json',J.P/'joint/candidate.nes',J.P/'joint/candidate.dbg',J.P/'joint/cf-stream.bin',J.P/'joint/cf-cookie.bin',R/'build/contra-force-lifecycle-isr-controls-v1/controls.json',Q.K/'build-proof.json',Q.P/'source-stage.json',Path(Q.__file__),R/'build/contra-force-shared-transport-isr-controls-v1/controls.json',R/'build/contra-force-shared-transport-isr-controls-v2/controls.json',R/'build/contra-force-shared-nmi-input-witness-v1/witness.json']
  out['bindings']={str(p.resolve()):sha(p)for p in paths};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],failure=out.get('failure'),cases=out['checks'].get('real_vector_cases'))),flush=True)
if __name__=='__main__':main()
