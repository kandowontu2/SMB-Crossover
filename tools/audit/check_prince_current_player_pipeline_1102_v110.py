"""Current full-cold head/side/source-control pipeline qualification."""
from pathlib import Path
from types import SimpleNamespace
import hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import check_prince_player_pipeline_1102_v67 as OLD
import check_prince_current_respawn_1102_v100 as C
O=C.O


def main():
 _,q=C.C.image();adapter=SimpleNamespace(PIN=q['parent_memory_SHA256'],sha=C.C.M.sha)
 text=inspect.getsource(OLD.main).replace('b,seed,lab=loaded()','b,seed,lab=CURRENT_LOADED()').replace('v67','v110').replace('native-manifest-v65.json','post-return-manifest-v97.json').replace('native-ingress-CPU-v66.json','current-native-ingress-CPU-v108.json')
 env=dict(OLD.__dict__,M=adapter,CURRENT_LOADED=C.loaded,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 p=O/'player-pipeline-CPU-v110.json';out=json.loads(p.read_text());assert out['passed']
 out.update(qualified_current_full_cold=True,scope='Actual current Prince97 over Bub66: complete full shared cold and original constructor, followed by960 genuine PlayerCtrlRoutine updates across flatRight, flatUp and wallUp metatile fixtures. Exact original phase/control/head/side callbacks execute; lives2/HP5/engine8 remain. Explicit CPU world/input preconditions only, no outcomes or emulator seeds. Does not prove native1-1 or helper crossing.')
 out['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(OLD.__file__),Path(C.__file__),O/'post-return-manifest-v97.json']});p.write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'player-pipeline-negative-v110.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
