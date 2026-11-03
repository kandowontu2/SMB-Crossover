"""Current159 truefirst8 then original contact/pit, death/cold/respawn."""
from pathlib import Path
from types import SimpleNamespace
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_respawn_1102_v93 as V
import check_prince_backdrop_native_1103_v160 as HOST
N,O=V.N,V.O


def main():
 source=inspect.getsource(V.main).replace('v93','v173')
 source=source.replace("'KillPlayer','PlayerLoseLife','MegaManDeathUpdate'","'KillPlayer','MegaManDeathStart','UnionDeathStartCore','PlayerLoseLife','MegaManDeathUpdate'")
 source=source.replace("assert events['KillPlayer']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None","assert events['KillPlayer']==(1 if case=='contact'else 0)and events['MegaManDeathStart']==events['UnionDeathStartCore']==events['PlayerLoseLife']==1 and life_epoch is not None and resumed is not None")
 marker="   if case=='contact':S.fatal(m,b)";assert marker in source
 source=source.replace(marker,"   S.C.C.terrain(m,lambda x,y:0x54 if y>=208 else 0)\n   N.invoke(m,'GameLoop',a=83,x=0,y=0,p=0x21) # Real first8 precedes any actual live enemy contact.\n"+marker)
 invoke=inspect.getsource(N.invoke).replace('range(500000)','range(4000000)').replace('c=NesMPU(','c=LIVE_N.NesMPU(');helper=dict(N.__dict__,LIVE_N=N);exec(compile(invoke,str(Path(N.__file__)),'exec'),helper);prior=N.invoke;N.invoke=helper['invoke']
 try:
  adapter=SimpleNamespace(loaded=HOST.loaded,__file__=str(Path(HOST.__file__)));env=dict(V.__dict__,C=adapter,__file__=str(Path(__file__)));exec(compile(source,str(Path(V.__file__)),'exec'),env);env['main']()
 finally:N.invoke=prior
 path=O/'post-return-respawn-CPU-v173.json';q=json.loads(path.read_text());q.update(source_code_injected_after_old_authenticated_cold=False,changed_full_cold_manager_not_qualified=False,memory_SHA256=HOST.M.image()[1]['expected_memory_only_SHA256'],real_first8_before_live_contact=True,scope='Actual159 complete residentcold/header image, then genuine first8 sourceconstructor before livecollision can occur. Originalcontact or unsupportedterrain, realGameLoop/nativeKill/nativeDeathStart/life2to1/InitializeArea/fulltypedcold/originalconstructor/entrance/right>=16 execute. No nativeengine/life/deathage outcome writes, no sourcecode injection; isolated CPUworld/enemy/timer/input preconditions. Native emulator/fullstage remain pending.')
 q['bindings'].update({p.relative_to(R).as_posix():HOST.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),Path(HOST.__file__),O/'backdrop-manifest-v159.json',O/'walk-oam-CPU-v167.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
