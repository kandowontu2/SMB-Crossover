"""Complete native item/body consumers on final130 cold and exact policies."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_native_ingress_1102_v108 as V
import check_prince_strike_cold_1103_v131 as C
O=C.O


def main():
 source=Path(V.__file__);text=inspect.getsource(V.main).replace('v108','v138')
 text=text.replace('C.M.sha','C.M.M.sha').replace('C.M.A.','C.M.M.A.')
 for old,new in {'post-return-manifest-v97.json':'strike-manifest-v130.json','native-labels-v78.json':'native-labels-v122.json','post-owner-v97.lbl':'post-owner-v130.lbl','current-foreign-hot-CPU-v103.json':'current-foreign-hot-CPU-v132.json','current-shared-cold-CPU-v99.json':'current-shared-cold-CPU-v131.json','current-game-loop-ISR-CPU-v102.json':'current-game-loop-ISR-CPU-v135.json'}.items():text=text.replace(old,new)
 env=dict(V.__dict__,__file__=str(Path(__file__)),C=C);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'current-native-ingress-CPU-v138.json';q=json.loads(path.read_text());assert q['passed']
 q.update(memory_only_SHA256=C.image()[1]['expected_memory_only_SHA256'],scope='Exact cf7+Prince130, complete actual sharedcold and originalFresh; whole nativePowerUpObjHandler four types and nativePlayerEnemyCollision three original sword modes/four actions, raw/header rejects. Source/native predicate fixture inputs only; no source-code injection, native outcomes/emulator/menu/fullstage claim. Original typed audio events preserved; native audio mapping remains unfinished.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.M.sha(p.read_bytes())for p in [Path(__file__),source,Path(C.__file__),O/'strike-manifest-v130.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
