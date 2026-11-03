"""Original contact/pit to native death/full cold/control on actual130."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_respawn_1102_v93 as V
import check_prince_strike_cold_1103_v131 as C
N,O=V.N,C.O


def main():
 source=Path(V.__file__);text=inspect.getsource(V.main).replace('v93','v133')
 text=text.replace("'KillPlayer','PlayerLoseLife','MegaManDeathUpdate'","'KillPlayer','MegaManDeathStart','UnionDeathStartCore','PlayerLoseLife','MegaManDeathUpdate'")
 text=text.replace("assert events['KillPlayer']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None","assert events['KillPlayer']==(1 if case=='contact'else 0)and events['MegaManDeathStart']==events['UnionDeathStartCore']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None")
 invocation=inspect.getsource(N.invoke);assert invocation.count('range(500000)')==1
 invocation=invocation.replace('range(500000)','range(4000000)').replace('c=NesMPU(','c=LIVE_N.NesMPU(')
 helper=dict(N.__dict__,LIVE_N=N);exec(compile(invocation,str(Path(N.__file__)),'exec'),helper);prior=N.invoke;N.invoke=helper['invoke']
 try:
  env=dict(V.__dict__,__file__=str(Path(__file__)),C=C);exec(compile(text,str(source),'exec'),env);env['main']()
 finally:N.invoke=prior
 path=O/'post-return-respawn-CPU-v133.json';q=json.loads(path.read_text());_,manifest=C.image()
 assert all(s['final_lives']==1 and s['final_engine']==8 and s['final_x']>=s['resumed_x']+16 for s in q['scenarios'])
 q.update(source_code_injected_after_old_authenticated_cold=False,changed_full_cold_manager_not_qualified=False,qualified_current_shared_cold_and_respawn=True,memory_only_SHA256=manifest['expected_memory_only_SHA256'],scope='Actual final130 cf7-pinned shared cold/header image before each case; genuine original contact and unsupported terrain, completeGameLoop/native death/life2to1/InitializeArea retirement/full typed cold/original constructor/control resumeRight>=16px. No engine/death-age/life outcomes seeded. No source-code injection, ROM/menu/emulator/fullstage claim.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.M.sha(p.read_bytes())for p in [Path(__file__),source,Path(C.__file__),O/'current-shared-cold-CPU-v131.json',O/'strike-manifest-v130.json',O/'native-labels-v122.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
