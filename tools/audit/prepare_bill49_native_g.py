"""Correct missed native arena placements; preserve the death-publication gap.

No private gameplay code changes. The original E collector, negative, checker
and source oracle stay intact. G uses the same oracle and strict checker.
"""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
E = R/'build/verification/agent49o2-bill-shape-components-e'
G = R/'build/verification/root49-bill-native-g'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
info = lambda p: dict(bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
    assert not G.exists()
    sys.dont_write_bytecode=True
    freeze=E/'freeze.json'
    assert sha(freeze)=='587b843c998cb1d9bf6eb822df5a030ac7e612d23b48a74fd56a401019ae42c9'
    for n,p in json.loads(freeze.read_text())['files'].items():
        assert info(E/n)==p
    negative=R/'build/verification/root49s2-e-bill-full-m3-a-review.json'
    result=json.loads(negative.read_text())
    assert result['status']=='FAIL_UNADMITTED_NATIVE_COVERAGE'
    assert not result['source_projection_mismatches'] and len(result['missing_actual_paths'])==10
    names=['common.py','source_model.py','bind_native.py','native.lua','check_native.py','run_native.py']
    texts={n:(E/n).read_text()for n in names}
    def replace(n,old,new):
        assert texts[n].count(old)==1,(n,old)
        texts[n]=texts[n].replace(old,new)
    replace('native.lua',"if spec.roof then tile((spec.x//16)*16+16,spec.roof,0xc4)end",
        "if spec.roof then tile(((spec.x+8)//16)*16,spec.roof,0xc4)end -- actual native head column")
    replace('native.lua',"age=r('MmDeathAge'),hurt=", "age=r('MmDeathAge'),corpseAge=r('RgDeathTotal')+256*r('RgDeathTotal',1),corpseLanded=r('RgDeathLanded'),corpseDelay=r('RgDeathDelay'),collisionDisabled=r('DisableCollisionDet'),hurt=")
    replace('bind_native.py',"enemy={'id':21,'ctrl':9,'dx':8,'y':116},required=['Launch','BodySelector','Body','Collision']",
        "enemy={'id':21,'ctrl':9,'dx':8,'y':90},updates=2,required=['Launch','BodySelector','Body','Collision']")
    replace('bind_native.py',"enemy={'id':21,'ctrl':9,'dx':8,'y':136},required=['BodySelector','Body','Collision','Injury']",
        "enemy={'id':21,'ctrl':9,'dx':8,'y':90},required=['Launch','BodySelector','Body','Collision','Injury']")
    G.mkdir()
    for n,text in texts.items():
        if n.endswith('.py'):
            compile(text,str(G/n),'exec')
        (G/n).write_text(text)
    files={n:info(G/n)for n in names}
    (G/'freeze.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
    report=dict(status='PREPARED_NATIVE_ARENA_CORRECTIONS_NOT_EXECUTED',script_sha256=sha(__file__),
        original_freeze=dict(path=str(freeze.relative_to(R)),**info(freeze)),
        original_46_negative=dict(path=str(negative.relative_to(R)),**info(negative)),
        new_freeze=info(G/'freeze.json'),files=files,
        modifications=['Roof is seeded in actual native head column floor((PX+8)/16); the1802 page-seam case retains the same original cell.',
            'Overhead enemy control9 Y90 gives actual Y104..110, disjoint from standing PY112 top113. The two-update clear-band arena includes one real controller jump update.',
            'Chest injury control uses the same initially disjoint enemy for a longer actual jump approach and additionally requires the genuine Launch path before accepting injury coverage.',
            'Read-only corpse age/landed/delay and collision-disable fields added for lifecycle diagnosis.'],
        unchanged=['Source primary/rational/integer oracle','Strict register/stack/body/contact/terrain/water checker',
            'Both46-scenario variant lists','Death-parent publication coverage requirement','Actual bank/eight-byte hook guards',
            'Initial-arena-only emulated writes; no gameplay/PC/register/ROM changes or traversal claim'],
        runtime_changed=False, main_changed=False,
        expected_open_gate='The two death-parent cases remain unadmitted until actual native lifecycle/consumer analysis; their requirements are not waived.')
    (G/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],sha(G/'preparation.json'),flush=True)


if __name__=='__main__':
    main()
