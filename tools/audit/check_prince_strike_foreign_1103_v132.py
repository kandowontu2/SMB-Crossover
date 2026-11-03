"""Current cf7 foreign cold and every published callback against final130."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_foreign_1102_v103 as V
import check_prince_strike_cold_1103_v131 as C
O=C.O


def main():
 text=inspect.getsource(V.main).replace('v103','v132').replace('post-return-manifest-v97.json','strike-manifest-v130.json').replace('current-shared-cold-CPU-v99.json','current-shared-cold-CPU-v131.json')
 env=dict(V.__dict__,__file__=str(Path(__file__)),C=C);exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 path=O/'current-foreign-hot-CPU-v132.json';q=json.loads(path.read_text());assert q['actual_current_foreign_hot_pairs']==592
 q.update(scope='Exact cf7 parent versus final Prince130, including unchanged current Bub head/initial tier payload/cookie. Actual complete foreign cold on each side, then every37 published row across two C windows and four flag states. Full private/native/ZP/SMC/maps/PPU/AXYP/SP equality. No source injection, ROM/menu/install/native claim.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),Path(C.__file__)]});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
