"""Current full authenticated cold/retirement and actual GameLoop respawn."""
from pathlib import Path
import hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_respawn_1102_v93 as V
import check_prince_current_cold_1102_v98 as C
N,O=V.N,V.O


def loaded():
 base,q=C.image();m,out=C.cold(base,38)
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
 m[0x2001]=30
 return base,m,json.loads((O/'native-labels-v78.json').read_text())


def main():
 source=Path(V.__file__);text=source.read_text().replace('v93','v100').replace('C.loaded()','CURRENT_LOADED()')
 # A real Prince cold is about2M instructions. The prior500k utility bound
 # intentionally stopped v93 before the historical cold could complete.
 invocation=inspect.getsource(N.invoke);assert invocation.count('range(500000)')==1
 invocation=invocation.replace('range(500000)','range(4000000)').replace('c=NesMPU(','c=LIVE_N.NesMPU(')
 helper=dict(N.__dict__,LIVE_N=N);exec(compile(invocation,str(Path(N.__file__)),'exec'),helper);prior=N.invoke;N.invoke=helper['invoke']
 try:
  env=dict(__file__=str(Path(__file__)),__name__='prince_current_respawn_v100',CURRENT_LOADED=loaded);exec(compile(text,str(source),'exec'),env);env['main']()
 finally:N.invoke=prior
 path=O/'post-return-respawn-CPU-v100.json';q=json.loads(path.read_text());_,manifest=C.image()
 assert len(q['scenarios'])==2 and all(s['final_lives']==1 and s['final_engine']==8 and s['final_x']>=s['resumed_x']+16 for s in q['scenarios'])
 q.update(source_code_injected_after_old_authenticated_cold=False,changed_full_cold_manager_not_qualified=False,qualified_current_shared_cold_and_respawn=True,memory_only_SHA256=manifest['expected_memory_only_SHA256'],invocation_instruction_bound=4000000,scope='Actual current Prince97 headers/payload loaded through complete shared manager before either scenario. Real contact or unsupported terrain edge, complete GameLoop/NMI, original source death, unchanged native life decrement, InitializeArea retirement and full typed cold reload, source constructor, stage entrance and resumed Right≥16px all execute with no engine/death-age/life outcomes written. Explicit CPU initial world/enemy/timer/input fixtures; no ROM/menu/emulator/native1-1 claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,Path(C.__file__),O/'current-shared-cold-CPU-v99.json',O/'post-return-manifest-v97.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
