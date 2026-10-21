"""Advance an idle reference wait when the actual player is already stopped."""
from pathlib import Path
import csv
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
B=R/'build/roster-through-2-2/root49-samus-pacing-d-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not (D/'revision-e.json').exists()
    text=(D/'policy-b.lua').read_text()
    text=text.replace('local cursor=1\n','local cursor=14853\nlocal idleFloor=1\n')
    anchor='for i=math.max(1,cursor-3),math.min(#ref,cursor+8)do'
    assert text.count(anchor)==1
    text=text.replace(anchor,'for i=math.max(1,idleFloor,cursor-3),math.min(#ref,cursor+8)do')
    anchor='local q=ref[best];local mask=q[18]\n'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+' if mask==0 and c.state==0 and c.vx==0 then idleFloor=best+1;cursor=idleFloor end\n')
    (D/'policy-e.lua').write_text(text)
    with (B/'inputs.csv').open(newline='') as f: data=[z for z in csv.DictReader(f) if int(z['poll'])<=14970]
    assert len(data)==14970
    p=D/'prefix-14970-e.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(data)
    (D/'revision-e.json').write_text(json.dumps(dict(status='PREPARED_IDLE_REFERENCE_CONTROLLER_CORRECTION',
        script_sha256=sha(__file__),prefix_sha256=sha(p),policy_sha256=sha(D/'policy-e.lua'),
        retained_D_negative='D passes the first castle firebar after the supported48-poll wait, then stops safely atX720/Y112. Reference matching repeatedly reselects the same stationary-mask row14863 and hits its180-poll controller bound.',
        correction='When the actual player is stopped on support and the proposed reference input is empty, advance a floor on reference search so its finite idle duration can elapse. All actions remain ordinary buttons.',
        no_runtime_or_emulated_state_changes=True,no_clear_claim=True),indent=2)+'\n')
    print('Prepared E idle pacing; D and its actual negative retained.')


if __name__=='__main__':main()
