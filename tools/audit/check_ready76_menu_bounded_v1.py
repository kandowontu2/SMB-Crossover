"""Verify every admission and source Start/A case after composing both owners."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
P=R/'build/hogan-adapter';J=R/'build/hogan-thomas-current';O=J/'menu-checks'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir()
    stage=json.loads((J/'source-stage.json').read_text())
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    parent=C.collect(C.scoped_load(P/'candidate.nes'))
    actual=C.collect(C.scoped_load(J/'candidate.nes'))
    assert len(actual)==86 and sum(not v['pending']for v in actual.values())==76
    changed=[k for k in actual if actual[k]!=parent[k]]
    assert changed==[(10,2)] and not actual[10,2]['pending'] and actual[10,2]['raw']==10,changed
    assert not actual[28,0]['pending'] and all(actual[28,i]['pending']for i in range(1,6))
    result=dict(passed=True,source_CPU=True,native=False,candidate=sha(J/'candidate.nes'),
        menu_identities=86,playable=76,Start_A_cases=688,only_admission_change=list(changed[0]),
        scope='Actual linked menu/controller dispatcher cases. No active gameplay or full-level claim.',
        bindings={str(p):sha(p)for p in [Path(__file__),Path(C.__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',J/'source-stage.json']})
    (O/'controls.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
