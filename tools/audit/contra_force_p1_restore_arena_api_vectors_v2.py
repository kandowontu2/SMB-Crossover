"""Allflag owned ROM-worker API + genuine busy NMI/IRQ cuts in CPU arena."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_p1_restore_arena_controls_v3 as A
V,F,Q,T,C,U=A.V,A.F,A.Q,A.T,A.C,A.U;O=R/'build/contra-force-p1-restore-arena-api-vectors-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def start(m,p=0x30):return C.start(A.arena(m),40960,219,a=87,x=2,y=3,p=p)
def comparable(m):return bytes(m[i]for i in range(32768)if not 256<=i<=480 and i not in list(range(2016,2023))+[2026,32762])
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,actual_cartridge=False,resource_adopted=False,checks={})
 try:
  base=V.scene();rows=[]
  for marker in[0,1,128,192,193]:
   for flags in[v for v in range(256)if v&48==48]:
    b=C.clone(base);T.put(b,SmFreezeLastBlue=marker,SmFreezePalettePending=19,SmFreezeTurn=1);b[T.address(T.B,'SmFreezePalettePacket'):T.address(T.B,'SmFreezePalettePacket')+7]=[173]*7
    ref=C.clone(b);expected=Q.public(ref,6,p=flags);m=A.arena(b);c=start(m,flags);actual=T.finish(m,c)
    assert actual['AXYP']==expected['AXYP']and m.rawtags==ref.rawtags and T.smc(m)==T.smc(ref)
    assert [bytes(x)for x in m.ram]==[bytes(x)for x in ref.ram]and comparable(m)==comparable(ref),('nonprotocol/global application',marker,flags)
    assert bytes(m[481:512])==bytes(ref[481:512])
    if marker in[192,193]:
     assert [T.get(m,n)for n in['SmFreezeLastBlue','SmFreezePalettePending','SmFreezeTurn']]==[192,192,1]
     assert list(m[T.address(T.B,'SmFreezePalettePacket'):T.address(T.B,'SmFreezePalettePacket')+7])==[63,21,3,26,48,39,0]
    else:
     assert [T.get(m,n)for n in['SmFreezeLastBlue','SmFreezePalettePending','SmFreezeTurn']]==[marker,19,1]
     assert list(m[T.address(T.B,'SmFreezePalettePacket'):T.address(T.B,'SmFreezePalettePacket')+7])==[173]*7
    rows.append(dict(marker=marker,P=flags,AXYP=actual['AXYP'],minimum_SP=actual['minimum_SP']))
  out['checks']['all64flags_each5owner_markers']=rows
  cuts=[];b=C.clone(base);T.put(b,SmFreezeLastBlue=193,SmFreezePalettePending=128,SmFreezeTurn=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,NmiDisable=255,ReloadCHRBank=0)
  b[T.address(T.B,'VRAM_Buffer1')]=0;b[21028]=128;m=A.arena(C.clone(b));c=start(m);e=A.arena(C.clone(b));ec=start(e);expected=T.finish(e,ec);seen=set()
  while c.pc!=32767:
   if m.rawtags[1]==219 and 40960<=c.pc<41027 and c.pc not in seen:
    seen.add(c.pc)
    for kind in['NMI','IRQ']:
     if kind=='IRQ'and c.p&4:continue
     z,d=U.clone(m,c);A.arena(z);before_ISR=list(z[:32768]);nw=len(z.writes);proof=U.interrupt(z,d,kind,keep_ppu=False);after_ISR=list(z[:32768]);isr_writes=z.writes[nw:];effect=[i for i,(a,b)in enumerate(zip(before_ISR,after_ISR))if a!=b];protocol=list(range(2016,2023))+[2026,32762,32760,32761,32759,T.address(T.B,'AreaType')]
     assert not any(at in protocol for at,v in isr_writes),('native busy ISR overlaps protocol/read inputs',c.pc,kind,isr_writes)
     expected_global=list(e[:32768])
     for at in effect:expected_global[at]=after_ISR[at]
     actual=T.finish(z,d)
     assert actual['AXYP']==expected['AXYP']and z.rawtags==e.rawtags and T.smc(z)==T.smc(e)
     assert [bytes(x)for x in z.ram]==[bytes(x)for x in e.ram]
     mismatch=[i for i in range(32768)if not 256<=i<=480 and z[i]!=expected_global[i]]
     assert not mismatch,('continuation differs beyond measured native ISR event',c.pc,kind,mismatch)
     assert list(z[T.address(T.B,'SmFreezePalettePacket'):T.address(T.B,'SmFreezePalettePacket')+7])==list(e[T.address(T.B,'SmFreezePalettePacket'):T.address(T.B,'SmFreezePalettePacket')+7])
     cuts.append(dict(PC=c.pc,SP=c.sp,measured_native_ISR_changed_addresses=effect,native_ISR_protocol_overlap=False,**proof))
   c.step()
  normal=F.normal(m);assert normal['paletteP1']==[26,48,39]
  out['checks']['actual_busy_foreground_vectors']=dict(cases=len(cuts),source_instruction_cuts=len(seen),rows=cuts,committed_normalNMI=normal)
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(A.__file__),A.A/'proof.json',A.A/'worker.bin',V.P/'source-stage.json',V.P/'joint/candidate.nes',R/'build/contra-force-p1-restore-arena-controls-v3/controls.json',R/'build/contra-force-p1-restore-arena-api-vectors-v1/controls.json',R/'build/contra-force-p1-restore-vector-diagnostic-v2/diagnostic.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'),vector_cases=out['checks'].get('actual_busy_foreground_vectors',{}).get('cases'))),flush=True)
if __name__=='__main__':main()
