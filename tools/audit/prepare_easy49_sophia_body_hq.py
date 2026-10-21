"""Avoid a second bank switch for the existing Ryu body projection."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-sophia-source-body-hl'
D = V / 'root49-sophia-source-body-hq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    prior = json.loads((P/'preparation.json').read_text())
    S = D/'source'
    for n,h in prior['source_sha256'].items():
        assert sha(P/'source'/n)==h,n
        p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
    shutil.copytree(P/'source/build/generated',S/'build/generated')
    path=S/'src/sophia_source_body.s'
    text=path.read_text()
    a='.segment "SOPHIA_BODY_COLD"\nSophiaSourceBodyStart:'
    assert text.count(a)==1;text=text.replace(a,'.segment "LEGACY_COLD"\nSophiaSourceBodyStart:')
    assert text.count('  farcall RyuSourceBodyBox, jmp')==1
    text=text.replace('  farcall RyuSourceBodyBox, jmp','  jmp RyuSourceBodyBox')
    first=text.index('.proc SophiaSourceFlatBodyValid')
    last=text.index('.endproc',first)+len('.endproc')
    valid=text[first:last].replace('SophiaSourceFlatBodyValid','SophiaFirebarFlatBodyValid')
    a='.proc CrossoverSourceFirebarDisjoint'
    assert text.count(a)==1
    text=text.replace(a,'SophiaSourceBodyEnd:\n.segment "SOPHIA_BODY_COLD"\nSophiaSourceFirebarStart:\n'+valid+'\n\n'+a)
    # Only the firebar call after its procedure label uses the local duplicate.
    at=text.index('.proc SophiaSourceFirebarDisjoint')
    text=text[:at]+text[at:].replace('jsr SophiaSourceFlatBodyValid','jsr SophiaFirebarFlatBodyValid')
    assert text.count('SophiaSourceBodyEnd:')==2
    pos=text.rindex('SophiaSourceBodyEnd:')
    text=text[:pos]+text[pos:].replace('SophiaSourceBodyEnd:','SophiaSourceFirebarEnd:',1)
    path.write_text(text)
    driver=(P/'build-driver.py').read_text()
    assert driver.count(repr(str(P/'source')))==1
    (D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
    record=dict(status='PRIVATE_PLACEMENT_OPTIMIZATION_PREPARED_NOT_ADMITTED',
        parent_preparation_sha256=sha(P/'preparation.json'),
        parent_compiled_geometry_sha256=sha(P/'compiled-geometry-ho.json'),
        parent_native_HP={m:sha(P/('native-hp-'+m)/'actual.json')for m in ['mmc3','mmc5']},
        source_sha256={n:sha(S/n)for n in prior['source_sha256']},
        changed_from_HL=['src/sophia_source_body.s'],script_sha256=sha(__file__),
        reason='Put body dispatcher, projection and validator in existing bank11 tail alongside RyuSourceBodyBox. Ryu no longer incurs a second bank switch; Sophia also projects with one ordinary farcall. Firebar gets a byte-identical A-only validator in its own3A tail.',
        phase_ceiling_bytes=500000000,workspace_ceiling_bytes=60000000000,
        RAM_added=0,main_changed=False, scope=prior['scope'])
    (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(status=record['status'],sources=len(record['source_sha256']))))


if __name__=='__main__':main()
