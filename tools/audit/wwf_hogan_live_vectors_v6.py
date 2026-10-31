"""Actual loaded typed punch/constructor and live real vector proof."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_hogan_natural_controls_v9 as N
import wwf_hogan_runtime_controls_v3 as V
from wwf_first_hogan_owner_isr_v1 import interrupt
from ff_wram_host_isr_v4 import clone
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address,location
H=V.H;T=V.T;J=N.J;O=R/'build/wwf-hogan-live-vectors-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def finish(m,c,hook=None):
 return H.finish(m,c,hook)

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,source_CPU_API_fixture=True,rows=[])
 try:
  b=T.qualified(J/'candidate.nes');V.J=J;m=V.make(b)
  # Genuine source turn/intro are driven by real translated controller input.
  for age in range(115):
   keys=1 if 75<=age<105 else 0
   H.put(m,SavedJoypadBits=keys,A_B_Buttons=0,PreviousA_B_Buttons=0)
   H.invoke(m,'HuMovement')
  px=H.get(m,'Player_X_Position')
  for n,z in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=(px+24)&255,Enemy_PageLoc=0,Enemy_Y_Position=176,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=0,Enemy_MovingDir=2).items():m[address(b,n)]=z
  hits=[];shots=[];minimum=224
  entries={address(b,n):n for n in ['WfMovement','WfRawProxyCommit','WfRuntimeReturnC','WfRuntimeReturnOriginal','WfResolve','ShellOrBlockDefeat','WfHostFrame']}
  for age in range(60):
   keys=64 if age==0 else 0
   H.put(m,SavedJoypadBits=keys,A_B_Buttons=keys,PreviousA_B_Buttons=64 if age==1 else 0)
   seen=set()
   def watch(mem,cpu,step):
    nonlocal minimum
    minimum=min(minimum,cpu.sp)
    if cpu.pc==address(b,'ShellOrBlockDefeat'):hits.append([age,cpu.x,mem.ram[2][0x7a],mem.ram[2][0x3c]])
    if age!=21:return
    raw=mem.rawtags[(cpu.pc-32768)//8192]if cpu.pc>=32768 else -1
    op=bytes(mem[cpu.pc:cpu.pc+3]);key=(raw,cpu.pc)
    reason=entries.get(cpu.pc)
    if op in[b'\x8d\x15\x51',b'\x8d\x16\x51']:reason='pending-map'
    if reason and key not in seen:seen.add(key);shots.append((reason,*clone(mem,cpu)))
   c,lo=H.invoke(m,'HuMovement',hook=watch)
  assert len(hits)==1 and hits[0][2]==198 and m[address(b,'Enemy_State')]&32,hits
  q['genuine_source_punch']=dict(passed=True,hits=hits,frames=60,minimum_foreground_SP=minimum,fixture='Actual native enemy ABI arena. Actor tuple is supplied in native fields; no source action/health/code/Ready is preloaded. Original translatedB→action15 reaches its own damage opcode and real native defeat once.')
  for reason,s,c in shots:
   # Punch is already in flight and current held input is0. Real normal
   # ReadJoypads therefore leaves the source continuation controller-stable.
   for context in ['lag','normal','paused']:
    for kind in ['NMI','IRQ']:
     z,d=clone(s,c);H.put(z,NmiDisable=255 if context=='lag'else 0,GamePauseStatus=int(context=='paused'))
     if kind=='IRQ'and d.p&4:continue
     reference,rc=clone(s,c);H.put(reference,NmiDisable=255 if context=='lag'else 0,GamePauseStatus=int(context=='paused'))
     finish(reference,rc)
     own=[bytes(a)for a in z.ram[1:]]
     low=interrupt(z,d,kind)
     assert[bytes(a)for a in z.ram[1:]]==own
     finish(z,d)
     assert(d.a,d.x,d.y,d.p,d.sp)==(rc.a,rc.x,rc.y,rc.p,rc.sp),(reason,context,kind,'CPU')
     assert[bytes(a)for a in z.ram[1:]]==[bytes(a)for a in reference.ram[1:]],(reason,context,kind,'Source continuation')
     assert z[address(b,'Enemy_State')]==reference[address(b,'Enemy_State')]and z.rawtags==reference.rawtags
     assert bytes(z[0x15a:0x17b])==bytes(reference[0x15a:0x17b])
     q['rows'].append(dict(reason=reason,context=context,vector=kind,entrySP=c.sp,minimum_ISR_SP=low))
  assert q['rows']
  q.update(passed=True,candidate=sha(J/'candidate.nes'),cuts=len(q['rows']),minimum_ISR_SP=min(r['minimum_ISR_SP']for r in q['rows']))
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(N.__file__),Path(V.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json']}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in ['passed','candidate','cuts','minimum_ISR_SP','error']}))
if __name__=='__main__':main()
