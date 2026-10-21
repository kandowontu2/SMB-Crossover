"""Keep both character body projections in one existing cold bank."""
from pathlib import Path
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
P=V/'root49-sophia-source-body-hl'
D=V/'root49-sophia-source-body-hs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    prior=json.loads((P/'preparation.json').read_text());S=D/'source'
    for n,h in prior['source_sha256'].items():
        assert sha(P/'source'/n)==h,n
        p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
    shutil.copytree(P/'source/build/generated',S/'build/generated')
    p=S/'src/ryu_source_body.s';text=p.read_text()
    assert text.count('.segment "LEGACY_COLD"')==1
    p.write_text(text.replace('.segment "LEGACY_COLD"','.segment "SOPHIA_BODY_COLD"'))
    p=S/'src/sophia_source_body.s';text=p.read_text()
    assert text.count('  farcall RyuSourceBodyBox, jmp')==1
    p.write_text(text.replace('  farcall RyuSourceBodyBox, jmp','  jmp RyuSourceBodyBox'))
    driver=(P/'build-driver.py').read_text()
    assert driver.count(repr(str(P/'source')))==1
    (D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
    record=dict(status='PRIVATE_SINGLE_BANK_BODY_PREPARED_NOT_ADMITTED',
        parent_preparation_sha256=sha(P/'preparation.json'),
        source_sha256={n:sha(S/n)for n in prior['source_sha256']},
        changed_from_HL=['src/ryu_source_body.s','src/sophia_source_body.s'],
        script_sha256=sha(__file__),RAM_added=0,main_changed=False,
        reason='Relocate existing Ryu body/platform cold procedures together into old3A FF tail, beside Sophia projection/dispatcher. All callers already use bank-aware farcalls; internal near calls remain within the same bank. One ordinary body bank fetch per character. Existing algorithm is unchanged.',
        retained_Q_negative='Q mapper3 placement fits but mapper5 bank11 tail overflows125B. Its failed layout/checker receipts are retained. This candidate uses the actual free tail common to both mappers.',
        phase_ceiling_bytes=500000000,workspace_ceiling_bytes=60000000000,scope=prior['scope'])
    (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(status=record['status'],sources=len(record['source_sha256']))))


if __name__=='__main__':main()
