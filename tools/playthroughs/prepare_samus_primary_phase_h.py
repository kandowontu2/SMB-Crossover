"""Retain the incompatible two-bar wait and test primary-hazard timing alone."""
from pathlib import Path
import csv
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
B=R/'build/roster-through-2-2/root49-samus-pacing-g-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not (D/'revision-h.json').exists()
    with (B/'phase-wait-g.csv').open(newline='') as f:z=list(csv.DictReader(f))
    matched=[r for r in z if r['poll']=='16453']
    assert [(r['targetX'],r['error']) for r in matched]==[('1348','0'),('1412','1792')]
    text=(D/'policy-g.lua').read_text()
    anchor=',{27,1412,68,16,224,0,256}'
    assert text.count(anchor)==1
    text=text.replace(anchor,'').replace('phase-wait-g.csv','phase-wait-h.csv')
    (D/'policy-h.lua').write_text(text)
    with (B/'inputs.csv').open(newline='') as f:data=[r for r in csv.DictReader(f) if int(r['poll'])<=16452]
    assert len(data)==16452
    p=D/'prefix-16452-h.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(data)
    (D/'revision-h.json').write_text(json.dumps(dict(status='PREPARED_PRIMARY_ONLY_PHASE_CONTROLLER_HYPOTHESIS',
        script_sha256=sha(__file__),prefix_sha256=sha(p),policy_sha256=sha(D/'policy-h.lua'),
        retained_G_negative='The two bars have different relative birth phases. At exact primary alignment the secondary remains1792 phase units away. Joint wait reaches its400-poll controller bound safely; no runtime defect or clear claim.',
        hypothesis='Time the primary hazard crossing with ordinary inputs, observe the secondary separately. This is an experiment, not a relaxed verification oracle.',
        emulated_writes=False,runtime_changes=False,no_clear_claim=True),indent=2)+'\n')
    print('Prepared primary-only ordinary wait H; incompatible joint G is retained.')


if __name__=='__main__':main()
