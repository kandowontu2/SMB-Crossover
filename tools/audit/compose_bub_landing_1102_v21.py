"""Root-approved exact private three-span landing successor; no installation."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

O=L.O;R=L.R;P=L.P
MANIFEST='061172eb97e12a3303553e10e06df81274e5a3d032e5cef6205ade2a4f851351'

def main():
    path=O/'landing-v21-proposal.json';assert P.sha(path.read_bytes())==MANIFEST
    q=json.loads(path.read_text());assert q['passed']and q['base_ROM_sha256']==L.PIN
    for rel,z in q['files'].items():assert P.sha((R/rel).read_bytes())==z['SHA256'],rel
    raw=L.CURRENT.read_bytes();assert P.sha(raw)==L.PIN;out=bytearray(raw);legal=set()
    for z in q['patches']:
        at=z['offset'];before=bytes.fromhex(z['old']);after=bytes.fromhex(z['new'])
        assert len(before)==len(after)and out[at:at+len(before)]==before
        assert not legal&set(range(at,at+len(before)));legal.update(range(at,at+len(before)))
        out[at:at+len(after)]=after
    actual={i for i,(a,b)in enumerate(zip(raw,out))if a!=b}
    assert len(actual)==370 and actual<=legal and P.sha(out)==q['expected_candidate_sha256']
    target=O/'combined-landing.nes';assert not target.exists();target.write_bytes(out)
    for suffix in['.dbg','.lbl']:
        (O/('combined-landing'+suffix)).write_bytes(L.CURRENT.with_suffix(suffix).read_bytes())
    receipt=dict(passed=True,private_candidate=True,installed=False,native=False,production_admitted=False,
        ROM=target.relative_to(R).as_posix(),ROM_sha256=P.sha(out),base_ROM_sha256=L.PIN,manifest_SHA256=MANIFEST,
        approval='Root explicitly approved privatev21 three exact-preimage spans after reading18B landing/10B dead telemetry source, verifying10frozenfiles and reconstructing expectedbe8095fd. No new resources; preserveallforeign/menu/currentbytes.',
        actual_changed_bytes=370,exact_patches=q['patches'],passed_minimal_DBG_copied_exact=True,
        private_actual_labels='build/bub-menu-candidate-1102-v2/landing-v21-layout.json',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),path,L.CURRENT,target,target.with_suffix('.dbg'),target.with_suffix('.lbl')]})
    (O/'combined-landing.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items()if k not in['exact_patches','bindings']}))

if __name__=='__main__':main()
