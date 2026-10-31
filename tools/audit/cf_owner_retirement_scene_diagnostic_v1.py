"""Retained parent/new genuine InitScreen sprite-clear callsite diagnostic."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_owner_retirement_coverage_v1 as V
T=V.T;C=V.C
O=R/'build/cf-owner-retirement-scene-diagnostic-v1'
def main():
 O.mkdir(exist_ok=False);rows=[]
 for root in[V.P/'joint',V.J]:
  m=V.loaded(root,0);T.put(m,SelectedCharacter=27,FmGroups=0,FmAlts=0,FfVariant=0,OperMode=1,OperMode_Task=1,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,CurrentPlayer=0)
  c=C.start(m,T.address(T.B,'InitScreen'),(T.location(T.B,'InitScreen')-16)//8192|128)
  at=T.address(T.B,'MoveAllSpritesOffscreen');bank=(T.location(T.B,'MoveAllSpritesOffscreen')-16)//8192|128
  trace=[];clears=[]
  def watch(cpu,step):
   trace.append([step,cpu.pc,m.rawtags[:],cpu.sp,cpu.a,cpu.x,cpu.y])
   if len(trace)>45:del trace[0]
   if cpu.pc==at and m.rawtags[(at-0x8000)//8192]==bank:clears.append(dict(step=step,stack=list(m[0x100+cpu.sp+1:0x100+min(cpu.sp+30,255)]),trace=trace[:]))
  z=T.finish(m,c,watch);rows.append(dict(root=str(root),result=z,clears=clears))
 q=dict(passed=True,rows=rows,bindings={str(p.resolve()):V.sha(p)for p in[Path(__file__),Path(V.__file__),V.P/'joint/candidate.nes',V.P/'joint/candidate.dbg',V.J/'candidate.nes',V.J/'candidate.dbg']})
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(rows))
if __name__=='__main__':main()
