"""Try the intrinsic Easy Morph Ball below the observed upper firebar."""
from pathlib import Path
import csv
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
B=R/'build/roster-through-2-2/root49-samus-pacing-h-2-v0-mmc3'
T=R/'build/roster-through-2-2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not (D/'revision-k.json').exists()
    I=T/'root49-samus-pacing-i-2-v0-mmc3'
    J=T/'root49-samus-pacing-contact-j-2-v0-mmc3'
    assert (I/'trace.csv').read_bytes()==(J/'trace.csv').read_bytes()
    assert (I/'inputs.csv').read_bytes()==(J/'inputs.csv').read_bytes()
    with (J/'samus-firebar-contact-j.csv').open(newline='') as f:
        hit=[r for r in csv.DictReader(f) if r['event']=='FirebarHit']
    assert len(hit)==1 and hit[0]['frame']=='16568'
    h=hit[0];assert int(h['bodyT'])<=int(h['R7'])<=int(h['bodyB'])
    (D/'contact-review-j.json').write_text(json.dumps(dict(status='REPRODUCED_UPPER_FIREBAR_CONTACT_CONTAINER_OVERLAPS',
        trace_sha256=sha(J/'trace.csv'),inputs_sha256=sha(J/'inputs.csv'),observer_sha256=sha(D/'firebar-observer-j.lua'),event=h,
        qualification='Actual slot3 upper-bar point119/77 is inside the native player box113/56..127/81. No source bitmap/phase equivalence or collision defect is established.'),indent=2)+'\n')
    inner=(D/'policy-e.lua').read_text().replace('local cursor=14853\nlocal idleFloor=1\n','local cursor=16200\nlocal idleFloor=16200\n')
    (D/'policy-k-inner.lua').write_text(inner)
    text='''-- Ordinary Down enters intrinsic Easy Morph; Up later stands on safe floor.
local nextPolicy=dofile(INNER)
local crossing=true
local age=0
local standing=0
return function(c)
 if crossing then
  age=age+1
  assert(age<260,'Morph crossing controller bound')
  if age>16 then assert(c.r('SmBall')==1,'Actual intrinsic Morph Ball attained')end
  if c.x>=1450 and c.state==0 then crossing=false;standing=8
  else return{right=true,down=age<=8}end
 end
 if standing>0 then standing=standing-1;return{up=true}end
 assert(c.r('SmBall')==0,'Actual ordinary Up exits Morph Ball')
 return nextPolicy(c)
end
'''.replace('INNER',json.dumps((D/'policy-k-inner.lua').as_posix()))
    (D/'policy-k.lua').write_text(text)
    with (B/'inputs.csv').open(newline='') as f:z=[r for r in csv.DictReader(f) if int(r['poll'])<=16540]
    assert len(z)==16540
    p=D/'prefix-16540-k.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(z)
    (D/'revision-k.json').write_text(json.dumps(dict(status='PREPARED_ORDINARY_MORPH_CROSSING_HYPOTHESIS',
        script_sha256=sha(__file__),policy_sha256=sha(D/'policy-k.lua'),inner_sha256=sha(D/'policy-k-inner.lua'),prefix_sha256=sha(p),
        contact_review_sha256=sha(D/'contact-review-j.json'),
        rationale='The held higher jump also meets the independently phased upper bar. Try the existing Easy midair Morph profile on the lower H trajectory, then ordinary Up on safe support. No collision or physics edits.',
        emulated_writes=False,no_clear_claim=True),indent=2)+'\n')
    print('Exact J contact classified; intrinsic Morph crossing K prepared.')


if __name__=='__main__':main()
