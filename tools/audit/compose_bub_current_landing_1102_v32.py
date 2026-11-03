"""Exact Sunny16a9 + three approved Bub landing spans; default memory-only."""
import argparse,hashlib,json
from pathlib import Path

R=Path(__file__).resolve().parents[2];O=R/'build/bub-menu-candidate-1102-v2'
BASE='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'
SUNNY='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
PRIVATE='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'
COMBINED='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
MANIFEST='061172eb97e12a3303553e10e06df81274e5a3d032e5cef6205ade2a4f851351'
digest=lambda data:hashlib.sha256(data).hexdigest()
sha=lambda path:digest(Path(path).read_bytes())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--emit',action='store_true',help='Only after root approves exact private composition; never installs.');args=ap.parse_args()
    parent=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
    sunny_path=R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9/receipt.json'
    manifest=O/'landing-v21-proposal.json';proposal=O/'landing-rebase-v27-proposal.json'
    source=parent.read_bytes();assert digest(source)==BASE
    sunny=json.loads(sunny_path.read_text());landing=json.loads(manifest.read_text());approved=json.loads(proposal.read_text())
    assert sunny['passed']and sunny['installed']and sunny['base_ROM_SHA256']==BASE and sunny['ROM_sha256']==SUNNY
    assert sha(manifest)==MANIFEST and landing['base_ROM_sha256']==BASE and landing['expected_candidate_sha256']==PRIVATE
    assert approved['current_base_ROM_sha256']==SUNNY and approved['expected_rebased_ROM_sha256']==COMBINED
    assert approved['patches']==landing['patches']and approved['binding']['Sunny_checkpoint']==sha(sunny_path)
    assert len(sunny['patches'])==5 and len(landing['patches'])==3
    intervals=[];all_rows=[]
    for owner,rows in[('Delivered Sunny palette v9',sunny['patches']),('Approved private Bub landing v21',landing['patches'])]:
        for row in rows:
            a=row['offset'];old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new'])
            assert len(old)==len(new)and source[a:a+len(old)]==old
            assert all(a+len(old)<=left or right<=a for left,right in intervals)
            intervals.append((a,a+len(old)));all_rows.append((owner,row))
    # Rebuild the delivered parent in memory. Do not create a second parentROM.
    current=bytearray(source)
    for row in sunny['patches']:
        a=row['offset'];current[a:a+len(bytes.fromhex(row['new']))]=bytes.fromhex(row['new'])
    assert digest(current)==SUNNY
    target=bytearray(current)
    for row in landing['patches']:
        a=row['offset'];old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new'])
        assert target[a:a+len(old)]==old;target[a:a+len(new)]=new
    assert digest(target)==COMBINED
    allowed={i for row in landing['patches']for i in range(row['offset'],row['offset']+len(bytes.fromhex(row['new'])))}
    changed={i for i,(a,b)in enumerate(zip(current,target))if a!=b}
    assert len(changed)==370 and changed<=allowed
    for row in sunny['patches']:
        a=row['offset'];new=bytes.fromhex(row['new']);assert target[a:a+len(new)]==new
    # Exact copied-source5434B/art bytes are already bound in v21. No shared
    # instruction, menu, other character or owner allocation is added here.
    files=[Path(__file__),parent,parent.with_suffix('.dbg'),parent.with_suffix('.lbl'),sunny_path,manifest,proposal]
    out=dict(passed=True,source_recipe_review_only=not args.emit,ROM_written=False,native=False,installed=False,production_admitted=False,
        source_base_ROM_sha256=BASE,delivered_parent_sha256=SUNNY,old_private_parent_sha256=PRIVATE,
        expected_rebased_ROM_sha256=COMBINED,exact_Sunny_five_patches_preserved=True,
        patch_intervals_disjoint=True,actual_changed_bytes_over_delivered_parent=370,
        patches=landing['patches'],new_resources=False,
        native_scope='Privatebe809 current fullstage packet is owned byroot. This9cf composition has no native receipt and must be qualified before installation. No new allocation/menu/sharedcode changes.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in files})
    if args.emit:
        path=O/'combined-current-landing.nes';assert not path.exists();path.write_bytes(target)
        for suffix in['.dbg','.lbl']:
            dst=path.with_suffix(suffix);assert not dst.exists();dst.write_bytes(parent.with_suffix(suffix).read_bytes())
            assert dst.read_bytes()==(O/'combined-landing').with_suffix(suffix).read_bytes()
        out.update(source_recipe_review_only=False,ROM_written=True,ROM=path.relative_to(R).as_posix(),private_candidate=True)
        out['bindings'][path.relative_to(R).as_posix()]=sha(path)
        receipt=O/'combined-current-landing.json'
    else:receipt=O/'landing-current-v32-check.json'
    assert not receipt.exists();receipt.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k not in['patches','bindings']}))


if __name__=='__main__':main()
