"""Try a full held jump across the independently phased upper firebar."""
from pathlib import Path
import csv
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
B=R/'build/roster-through-2-2/root49-samus-pacing-h-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not (D/'revision-i.json').exists()
    inner=(D/'policy-e.lua').read_text().replace('local cursor=14853\nlocal idleFloor=1\n','local cursor=16160\nlocal idleFloor=16160\n')
    (D/'policy-i-inner.lua').write_text(inner)
    text='''-- Ordinary held A selects the existing full-height jump.
local nextPolicy=dofile(INNER)
local crossing=true
local age=0
return function(c)
 if crossing then
  age=age+1
  assert(age<240,'Held-jump controller bound')
  if c.x>=1450 and c.state==0 then crossing=false
  else return{right=true,a=true,b=c.poll%8<4}end
 end
 return nextPolicy(c)
end
'''.replace('INNER',json.dumps((D/'policy-i-inner.lua').as_posix()))
    (D/'policy-i.lua').write_text(text)
    with (B/'inputs.csv').open(newline='') as f:z=[r for r in csv.DictReader(f) if int(r['poll'])<=16521]
    assert len(z)==16521
    p=D/'prefix-16521-i.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(z)
    (D/'revision-i.json').write_text(json.dumps(dict(status='PREPARED_ORDINARY_HELD_JUMP_CONTROLLER_HYPOTHESIS',
        script_sha256=sha(__file__),policy_sha256=sha(D/'policy-i.lua'),inner_sha256=sha(D/'policy-i-inner.lua'),prefix_sha256=sha(p),
        retained_H_negative='Primary phase alignment passes its lower hazard, but reaches a different upper firebar phase and dies16559/X1373/Y75. No source-disjointness or runtime bug established.',
        hypothesis='Hold the existing jump button beyond the shorter reference release to pass higher over the independently phased upper bar; normal right/shoot inputs only.',
        emulated_writes=False,runtime_changes=False,no_clear_claim=True),indent=2)+'\n')
    print('Prepared ordinary held-jump experiment I.')


if __name__=='__main__':main()
