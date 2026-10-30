"""Freeze the source-qualified victory draw for a bounded native replay."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[1]
O=R/'build/rogue-dawn-victory-pose-v4'
P=R/'build/rogue-dawn-flagpole-v1'


def binding(path):
    p=Path(path).resolve()
    return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    assert not (O/'handoff.json').exists()
    inputs={}
    for path in [P/'handoff.json',O/'build.json',O/'controls.json',O/'caller-edges.json']:
        record=json.loads(path.read_text())
        assert record['passed']
        for b in record['bindings']:
            assert binding(b['path'])==b,b['path']
            inputs[b['path']]=b
        inputs[str(path)]=binding(path)
    inputs[str(Path(__file__))]=binding(__file__)
    record=dict(passed=True,source_CPU_qualified=True,native_run=False,shared_admission=False,
        ROM=binding(O/'candidate.nes'),bindings=list(inputs.values()),new_RAM=0,
        implementation='Authentic standing record8 during automatic SMB engine4/5 only; '
            'visibility permits these phases even if source action froze at literal F7 damage flash. '
            'Source animation/action/radii remain intact. Compact real two-call-site dispatch '
            'retains X and frees space for the visibility guard; incoming A/P are dead at both callers.',
        scope='1584 art/state cases;20 complete DrawAll and authentic pixel consumers; '
            '10 active Rogue Main/NMI;48 foreign Main/NMI;48 actual PLAYER collision callers;14 real ISR seams.',
        limitations=['Native exact-candidate victory presentation remains to be replayed.',
            'Rogue shared-menu admission, Hard/all-powerup/shortcut coverage and measured lag remain open.',
            'Standing castle animation is an explicit SMB adaptation; Rogue has no original castle sequence.'])
    (O/'handoff.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(passed=True,handoff=binding(O/'handoff.json'),inputs=len(inputs))))


if __name__=='__main__':main()
