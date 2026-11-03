"""Actual130 earned death/row8/star/1up real FF and hardware IRQ cuts."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_game_loop_isr_1102_v102 as V
import check_prince_strike_actual_1103_v134 as A
O=A.O


def main():
 A.bind();source=Path(V.__file__);text=inspect.getsource(V.main).replace('v102','v135')
 text=text.replace('minimum=224','minimum=224;i1=0',1).replace("cuts=V.fold_cuts(ref['cuts'])","cuts=A.U.V.fold(ref['cuts']);i1+=sum(bool(c[3])for c in cuts)")
 old='   for cut in cuts:\n    z=N.fork(seed)';new="   for cut in cuts:\n    if kind=='IRQ'and cut[3]:continue\n    z=N.fork(seed)";assert old in text;text=text.replace(old,new)
 env=dict(V.__dict__,__file__=str(Path(__file__)),A=A,environment=lambda:A.U.V.environment()[0]);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'current-game-loop-ISR-CPU-v135.json';q=json.loads(path.read_text());q.update(all_actual_FF_I1_cut_collection=True,scope='Exact source-backed130 cf7 image after actual full cold/header publication, no injected code. ActualGameLoop source-earned death, native row8 death update, actual native star and1up execute. Each recorded PC/A-bank/I-flag at deepest realSP is replayed with true hardware IRQ(I0only) and genuine FF-lag NMI(I0orI1). Every I1 foreground instruction is collected independently of old watched PC filters. Actual lag branch and oneINC/no regular branch asserted. Full private/R0..7/SMC/maps/AXYP/SP exact; native07DA is the source-tracked AudioUpdate counter. No ROM/menu/emulator/fullstage claim.')
 q['bindings'].update({p.relative_to(A.R).as_posix():A.C.M.M.sha(p.read_bytes())for p in [Path(__file__),source,Path(A.__file__),O/'strike-manifest-v130.json',O/'current-shared-cold-CPU-v131.json',O/'post-return-respawn-CPU-v133.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
