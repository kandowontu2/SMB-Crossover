"""Add the frozen missile-armor correction without moving combined code."""
from pathlib import Path
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
B=V/'root49-combined-working-b'
A=V/'agent49-samus-bill-arsenal-a'
D=V/'root49-combined-working-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    freeze=A/'missile-freeze-y/freeze.json'
    assert sha(freeze)=='ad06337c6cd8f898afc67967eb93e7719ebf5f02bd3bcb6bccfb3aa534e003e0'
    f=json.loads(freeze.read_text())
    receipt=A/'missile-freeze-y/receipt-catalog.json'
    assert sha(receipt)==f['receipt_catalog_sha256']=='e9b750094811086b23175a301625fd787cdb9f6cb0498315d54594b86ea660c8'
    cat=json.loads(receipt.read_text())
    assert len(cat)==295
    for n,h in cat.items():
        p=A/n
        assert p.stat().st_size==h['bytes'] and sha(p)==h['sha256'],n
    base=json.loads((B/'source-catalog.json').read_text())
    parent=json.loads((A/'source-catalog-f.json').read_text())
    newpath=A/'source-catalog-p.json'
    assert sha(newpath)==f['source_catalog_sha256']
    new=json.loads(newpath.read_text())
    assert len(base)==455 and set(base)==set(parent)==set(new)
    assert {n for n in new if new[n]!=parent[n]}=={'src/megaman_weapons.s'}
    assert base['src/megaman_weapons.s']==parent['src/megaman_weapons.s']
    for n in base:
        assert sha(B/'source'/n)==base[n],n
        assert sha(A/'source-p'/n)==new[n],n
        p=D/'source'/n
        p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile((A/'source-p' if n=='src/megaman_weapons.s' else B/'source')/n,p)
    generated=json.loads((B/'preparation.json').read_text())['generated11']
    for n,h in generated.items():
        p=B/'source/build/generated'/n
        assert sha(p)==h
        target=D/'source/build/generated'/n
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
    shutil.copyfile(B/'build.py',D/'build.py')
    merged={n:sha(D/'source'/n) for n in base}
    (D/'source-catalog.json').write_text(json.dumps(merged,indent=2)+'\n')
    result=dict(status='PREPARED_MISSILE_ARMOR_OVERLAY_OVER_COMBINED_B_NOT_BUILT',
        script_sha256=sha(__file__),source_catalog_sha256=sha(D/'source-catalog.json'),
        parent_composition_sha256=sha(B/'composition-review.json'),missile_freeze_sha256=sha(freeze),
        rehashed_receipts=295,source_files=455,changed_source='src/megaman_weapons.s',
        generated11=generated,phase_cap_bytes=500000000,final_reserve_bytes=50000000,global_cap_bytes=70000000000,
        qualifications=f['qualifications'],main_changed=False,goal_complete=False,accepted_release=False)
    (D/'preparation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','source_files','rehashed_receipts']}))


if __name__=='__main__':main()
