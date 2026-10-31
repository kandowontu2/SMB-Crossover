"""Actual busy-foreground CF palette/UI seams, and completed normal NMI flush."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_loader_isr_controls_v2 as U
import contra_force_palette_names_controls_v2 as V
Q,J,C,T=V.Q,V.J,V.C,V.T;U.B=T.B;O=R/'build/contra-force-palette-names-isr-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def entry(m,service):return C.start(m,T.address(T.B,'BtServiceVeneers')+3*service,215,a=(1 if service==30 else 0),x=29,y=(30 if service==30 else 0),p=0x31)
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,checks={})
 try:
  base=Q.load(0);Q.public(base,15);rows=[];normal=[]
  for svc in [26,29,30,17,18]:
   b=V.seed(base);T.put(b,VRAM_Buffer_AddrCtrl=0,Sprite0HitDetectFlag=0,ReloadCHRBank=0,NmiDisable=255,SavedJoypadBits=0);m=C.clone(b);c=entry(m,svc)
   e=C.clone(b);ec=entry(e,svc);expected=T.finish(e,ec);seen=set()
   while c.pc!=32767:
    pc=c.pc;raw=m.rawtags[(pc-32768)//8192]if pc>=32768 else-1
    # Exact emitted source worker instruction cuts (including incomplete
    # queue/copy/ACK state). BusyMain permits lagNMI only, never a fabricated
    # normal publisher consuming a half-written foreground packet.
    if raw==3 and (Q.L['CfHostForcePalette']<=pc<Q.L['CfHostPaletteNamesEnd']or pc==Q.L['CfHostPortrait'])and pc not in seen:
     seen.add(pc)
     for kind in ['NMI','IRQ']:
      if kind=='IRQ'and c.p&4:continue
      z,d=U.clone(m,c);z[21028]=128;proof=U.interrupt(z,d,kind,keep_ppu=False);r=T.finish(z,d)
      assert r['AXYP']==expected['AXYP']and z.rawtags==e.rawtags and [bytes(x)for x in z.ram]==[bytes(x)for x in e.ram]
      assert V.queue(z)==V.queue(e),('ordered native queue after source continuation',svc,pc,kind)
      rows.append(dict(service=svc,PC=pc,SP=c.sp,**proof))
    c.step()
   # The committed foreground state can now legitimately publish NmiDisable0.
   # Normal vector consumes actual native queue through original full chain.
   T.put(m,NmiDisable=0);m[21028]=128;proof=U.interrupt(m,c,'NMI',keep_ppu=False)
   assert T.get(m,'VRAM_Buffer1_Offset')==0 and m.ram[2][0x2e2]==e.ram[2][0x2e2]
   normal.append(dict(service=svc,**proof))
  out['checks']=dict(actual_lagNMI_legalIRQ_instruction_cases=len(rows),completed_normalNMI_flush_cases=normal,fullAXYP_rawmaps_33SMC_livepage1_source_payload_nativequeue_exact=True,rows=rows)
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(V.__file__),Path(U.__file__),V.P/'source-stage.json',V.P/'joint/candidate.nes',V.K/'build-proof.json',V.O/'controls.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],cases=out.get('checks',{}).get('actual_lagNMI_legalIRQ_instruction_cases'),error=out.get('error'))),flush=True)
if __name__=='__main__':main()
