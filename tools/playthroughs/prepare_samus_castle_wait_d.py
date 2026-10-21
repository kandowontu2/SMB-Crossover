"""Classify the replayed contact and try an ordinary wait on safe castle support."""
from pathlib import Path
import csv
import hashlib
import json

R=Path(__file__).resolve().parents[2]
D=R/'build/verification/root49-samus-reference-pacing-a'
B=R/'build/roster-through-2-2/root49-samus-pacing-b-2-v0-mmc3'
C=R/'build/roster-through-2-2/root49-samus-pacing-contact-c-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))


def main():
    assert not (D/'contact-review-c.json').exists()
    # Every recorded trace column, including cycles, is identical in this fixed replay.
    assert (B/'trace.csv').read_bytes()==(C/'trace.csv').read_bytes()
    assert (B/'inputs.csv').read_bytes()==(C/'inputs.csv').read_bytes()
    hit=[r for r in rows(C/'samus-firebar-contact.csv') if r['event']=='FirebarHit']
    assert len(hit)==1 and int(hit[0]['frame'])==14745
    h=hit[0]
    body=[int(h[k]) for k in ('bodyL','bodyT','bodyR','bodyB')]
    x,y=int(h['R6']),int(h['R7'])
    container=[x-3,y-3,x+13,y+13]
    overlap=[max(body[0],container[0]),max(body[1],container[1]),min(body[2],container[2]),min(body[3],container[3])]
    assert overlap[0]<overlap[2] and overlap[1]<overlap[3]
    review=dict(status='REPRODUCED_CONTACT_NO_ESTABLISHED_SOURCE_DISJOINTNESS',
        trace_sha256=sha(C/'trace.csv'), inputs_sha256=sha(C/'inputs.csv'),
        observer_binding_sha256=sha(D/'firebar-binding-c.json'), event=h,
        current_native_body_box=body,conservative_part_container=container,positive_overlap=overlap,
        qualification='The conservative current-part container overlaps the player. This does not establish Flash bitmap/phase equivalence or certify the native collision. No runtime collision change is justified by this receipt.',
        no_emulated_state_writes=True,no_clear_claim=True)
    (D/'contact-review-c.json').write_text(json.dumps(review,indent=2)+'\n')
    prefix=D/'prefix-14687-d.csv'
    selected=[r for r in rows(B/'inputs.csv') if int(r['poll'])<=14687]
    assert len(selected)==14687
    with prefix.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['poll','frame','mask']);w.writeheader();w.writerows(selected)
    inner=(D/'policy-b.lua').read_text()
    assert inner.count('local cursor=1\n')==1
    inner=inner.replace('local cursor=1\n','local cursor=14620\n')
    (D/'policy-d-inner.lua').write_text(inner)
    wrapper='''-- A controller-only wait at the already observed supported X470/Y64.
local nextPolicy=dofile(INNER)
local waiting=48
return function(c)
 if waiting>0 then
  assert(c.world==0 and c.level==3 and c.y==64 and c.state==0,'Wait must retain real upper support')
  waiting=waiting-1
  return {}
 end
 return nextPolicy(c)
end
'''.replace('INNER',json.dumps((D/'policy-d-inner.lua').as_posix()))
    (D/'policy-d.lua').write_text(wrapper)
    (D/'revision-d.json').write_text(json.dumps(dict(status='PREPARED_48_POLL_CASTLE_WAIT_CONTROLLER_HYPOTHESIS',
        script_sha256=sha(__file__),prefix_sha256=sha(prefix),policy_sha256=sha(D/'policy-d.lua'),
        inner_sha256=sha(D/'policy-d-inner.lua'), contact_review_sha256=sha(D/'contact-review-c.json'),
        ordinary_wait_polls=48,emulated_writes=False,source_changes=False,no_clear_claim=True),indent=2)+'\n')
    print('Contact replay classified; ordinary supported wait D prepared.')


if __name__=='__main__':main()
