"""Actual new18B native-world far-tail and real SFC/map/vector seams."""
from pathlib import Path
import json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bt_jmp_row_cold_controls_v3 as A
L,H=A.L,A.H;J=R/'build/bt-native-world-source-v2/joint';O=R/'build/bt-native-world-isr-controls-v1'

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,vectors=[])
 try:
  b=H.C.qualified(J/'candidate.nes');seed=L.make(b);c,_=L.call(seed,'BtLoad');assert c.p&1
  H.put(seed,OperMode=0,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,FamilyMainCommit=1,VRAM_Buffer1_Offset=0)
  helper=A.address(b,'BtNativeWorldPalette');query=A.address(b,'HuNativeWorldPalette');cuts=[];seen=set()
  def trace(m,c,i):
   raw=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
   own=(raw==3 and helper<=c.pc<helper+18)or(raw==0xcf and query<=c.pc<query+13)or 0x15a<=c.pc<0x17b
   if own and(raw,c.pc)not in seen:seen.add((raw,c.pc));cuts.append((i,c.pc,bool(c.p&4)))
  m=A.fork(seed);base,lo,_=A.finish(m,A.start(m,32),trace);expected=(base.a,base.x,base.y,base.p,base.sp)
  for step,pc,masked in cuts:
   for kind,lag,pause in[('NMI',0,0),('NMI',255,0),('NMI',0,1)]+([]if masked else[('IRQ',255,0)]):
    m=A.fork(seed);H.put(m,NmiDisable=lag,GamePauseStatus=pause);proof=[]
    def inject(mm,c,i):
     if i==step:assert c.pc==pc;proof.append(L.V.interrupt(mm,c,kind))
    c,low,_=A.finish(m,A.start(m,32),inject)
    assert len(proof)==1 and(c.a,c.x,c.y,c.p,c.sp)==expected
    q['vectors'].append(dict(PC=pc,lag=lag,pause=pause,**proof[0]))
  assert any(r['PC']==helper for r in q['vectors'])
  q.update(passed=True,actual_cuts=len(cuts),actual_vectors=len(q['vectors']),minimum_ISR_SP=min(r['minimum_SP']for r in q['vectors']),all33SMC_livepage1_AXYP_SP_guestbanks_rawmaps_exact=True,actual_native_query_continuation_exact=True,scope='Stable zero-input title contexts for normal/paused; genuine lag/IRQ cuts. No input restoration, code trap or native emulator/readiness claim.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),Path(A.__file__),Path(L.__file__),Path(L.V.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/api.s',J/'bt/cache.bin',J/'bt/cookie.bin']
 q['bindings']={str(p.resolve()):L.sha(p)for p in files};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['vectors','bindings']}),flush=True);assert q['passed'],q.get('error')
if __name__=='__main__':main()
