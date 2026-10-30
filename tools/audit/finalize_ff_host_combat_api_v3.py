"""Clarify the volatile-V ABI without changing any qualified component bytes."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v3 as T
C=T.C;sha=T.sha
P=R/'build/final-fantasy-host-combat-qualified-v2/handoff.json'
O=R/'build/final-fantasy-host-combat-qualified-v3'

def main():
    assert not O.exists();O.mkdir();d=json.loads(P.read_text())
    for p,h in d['bindings'].items():assert sha(p)==h,p
    b=C.bundle(R/'build/final-fantasy-host-combat-v2');rows=[]
    for p in C.flags():
        m=T.make(b);T.actor(m);m.raw_page(1,3);T.setv(m,'CurrentBank',3)
        c,tr=T.direct(m,'FfHostTarget',x=0,p=p)
        assert c.p&1 and c.x==0 and c.p&12==p&12
        rows.append([p,c.p])
    # Genuine accepted geometry arithmetic clears V even when incoming V=1.
    assert any(p&64 and not out&64 for p,out in rows)
    d['API']['FfHostWeapons']=d['API']['FfHostWeapons'].replace('A/X/Y/N/Z/C volatile','A/X/Y/N/V/Z/C volatile')
    d['API']['FfHostTarget']=d['API']['FfHostTarget'].replace('A/Y/N/Z/C volatile','A/Y/N/V/Z/C volatile')
    d['counts']['native_defeat_indices_all64incoming_flags']=d['counts'].pop('native_defeat_indices_APXY64')
    d['ABI_clarification']='V2 handoff listed volatile flags incompletely for Target/Weapons. Actual geometry ADC/SBC changes V; it is volatile. No source or binary change. Defeat tests cover every incoming flag combination and native indices, without promising Damage preserves APXY. Only NewEnemy promises full APXY preservation.'
    proof=O/'volatile-V.json';proof.write_text(json.dumps(dict(passed=True,cases=64,rows=rows),indent=2)+'\n')
    for p in [P,Path(__file__),proof]:d['bindings'][str(p.resolve())]=sha(p)
    out=O/'handoff.json';out.write_text(json.dumps(d,indent=2)+'\n')
    for p,h in d['bindings'].items():assert sha(p)==h,p
    print(json.dumps(dict(passed=True,handoff=str(out),sha256=sha(out),bindings=len(d['bindings']),image_sha256=d['image_sha256'])))
if __name__=='__main__':main()
