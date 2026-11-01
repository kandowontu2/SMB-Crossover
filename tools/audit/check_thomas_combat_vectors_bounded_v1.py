"""Reproduce the genuine first melee defeat and interrupt its deepest CPU cut."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_thomas_all_pipes_bounded_v1 as A
C=A.C;Q=A.Q;T=A.T
J=R/'build/thomas-safe-melee';O=J/'combat-vectors'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir();q=dict(passed=False,source_CPU=True,native=False)
    try:
        stage=json.loads((J/'source-stage.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=C.scoped_load(J/'candidate.nes');syms=T.labels(J/'candidate.lbl')
        def factory(bundle):
            m=Q.ns['HostMemory'](bundle);m.observe(syms)
            m.frame_entry=syms['ThomasC2AcceptedFrame'];m.pending=None;m.actor_frames=0
            m.defeat_pc=syms['ShellOrBlockDefeat'];m.defeat_phase=False
            return m
        C.Bus=factory;C.NesMPU=A.CPU
        m=C.fresh(b);C.put(m,CrossoverMenuIndex=10,FmAlts=64,FmGroups=0)
        for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
        C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
        C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',a=0)
        def step(keys):
            m.defeat_phase=False
            C.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            z=C.invoke(m,'GameLoop');C.consume(m);return z
        for setup in range(600):
            if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
            step(0)
        else:raise AssertionError('Actual parser bound')
        for age in range(650):
            x=C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc')
            near=any(0<C.get(m,'Enemy_Flag',i)<128 and C.get(m,'Enemy_ID',i)==6 and not C.get(m,'Enemy_State',i)&32 and
                     0<C.get(m,'Enemy_X_Position',i)+256*C.get(m,'Enemy_PageLoc',i)-x<=38 for i in range(6))
            z=step((68 if age%24<6 else 4)if near else 1)
            if z['counts'].get('ShellOrBlockDefeat'):break
        else:raise AssertionError('Genuine melee defeat bound')
        q.update(parser_Main=setup,Main=age+1,original_actor_frame_pairs=m.actor_frames,combat_vectors=A.vectors())
        assert all(v['passed']for v in q['combat_vectors']),q['combat_vectors']
        q['passed']=True
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        q.update(candidate=sha(J/'candidate.nes'),scope='Actual cold/controller-byte native defeat plus real-code NMI/legal nested IRQ at the captured combat cut. CPU/peripheral model only; no native/raster/full-level claim.',
                 bindings={str(p):sha(p)for p in [Path(__file__),Path(A.__file__),Path(Q.__file__),Path(C.__file__),Q.observer,Q.oracle,J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']})
        (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}))


if __name__=='__main__':main()
