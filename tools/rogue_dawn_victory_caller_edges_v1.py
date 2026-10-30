"""Recheck both real collision call sites after the compact dispatch change."""
from pathlib import Path
import itertools
import json
import sys
import traceback

R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_flagpole_controls_v1 as base

O=R/'build/rogue-dawn-victory-pose-v4'
P=R/'build/rogue-dawn-flagpole-v1'
v,q,get,put,address=base.v,base.q,base.get,base.put,base.address


def main():
    assert not (O/'caller-edges.json').exists()
    build=json.loads((O/'build.json').read_text())
    for z in build['bindings']: assert v.ref.binding(z['path'])==z,z['path']
    old,b=v.scoped_load(P/'candidate.nes'),v.scoped_load(O/'candidate.nes')
    checks={}
    proof=dict(passed=False,source_CPU_only=True,native_run=False,checks=checks)
    try:
        rows=[]
        for mode,center,flags in itertools.product([0,1],[343,344,599,600],[0x30,0x31,0x70,0x71,0x34,0xf3]):
            pair=[]
            for bundle in [old,b]:
                m=base.fixture(bundle,center=center,mode=mode)
                put(m,SavedJoypadBits=0,RdGravity=0,Player_X_Speed=0)
                c,z=q.invoke(m,'PlayerCtrlRoutine',a=54,x=13,y=87,p=flags)
                assert get(m,'GameEngineSubroutine')==4
                assert sum(pc==address(bundle,'RdBoxOrExit') and bank==95 for pc,bank,sp in z['trace'])==2
                assert any(pc==address(bundle,'FlagpoleCollision') for pc,bank,sp in z['trace'])
                pair.append((base.registers(c),base.application(m),q.physical(m),z['CPU'],z['minimum_SP']))
            assert pair[0][:3]==pair[1][:3],('actual caller ABI',mode,center,flags)
            rows.append(dict(mode=mode,center=center,input_flags=flags,exact_application_registers_banks=True,
                             CPU_delta=pair[1][3]-pair[0][3],minimum_SP=pair[1][4]))
        checks['48_real_PLAYER_selector_then_BG_flagpole_transaction']=rows
        rows=[]
        seams=[('RdBoxOrExit',0),('RdBoxOrExit',3),('RdNonSolidBG',0),('RdNonSolidBG',2)]
        # GameEngineSubroutine uses LDA zero-page (2B); +3 is its following
        # CMP operand, not a legal instruction boundary. Retain negative1.
        for (name,offset),kind in itertools.product(seams,['NMI','IRQ']):
            m=base.fixture(b)
            put(m,SavedJoypadBits=0,RdGravity=0,Player_X_Speed=0,NmiDisable=255)
            c,z=q.invoke(m,'PlayerCtrlRoutine',a=54,x=13,y=87,p=0x71,
                         cut=(address(b,name)+offset,95,kind))
            assert get(m,'GameEngineSubroutine')==4 and z['minimum_SP']>=128
            rows.append(dict(cut=name,offset=offset,interrupt=kind,minimum_SP=z['minimum_SP'],
                             proof=q.summary(z['interrupt'])))
        checks['8_genuine_collision_dispatch_vector_ISR_seams']=rows
        proof.update(passed=True,ROM=v.ref.binding(O/'candidate.nes'),
                     bindings=[v.ref.binding(p) for p in [Path(__file__),O/'build.json',O/'controls.json',
                         P/'candidate.nes',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl']],
                     limits='CPU source/caller evidence; exact-candidate displayed victory still needs native review.')
    except Exception as e:
        proof.update(error=repr(e),traceback=traceback.format_exc())
        i=1
        while (O/f'caller-edges-negative-{i}.json').exists():i+=1
        (O/f'caller-edges-negative-{i}.json').write_text(json.dumps(proof,indent=2)+'\n')
        raise
    (O/'caller-edges.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,counts={k:len(v) for k,v in checks.items()})))


if __name__=='__main__':main()
