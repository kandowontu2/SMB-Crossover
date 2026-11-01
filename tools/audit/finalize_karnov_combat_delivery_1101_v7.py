"""Verify an installed combat checkpoint after its README encoding repair."""
from pathlib import Path
import hashlib,json,zipfile
from build_storage_guard_v1 import preflight
from deliver_karnov_menu_health_1101_v3 import validate

R=Path(__file__).resolve().parents[2];O=R/'build/karnov-delivery-finalize-1101-v7'
D=R/'docs/qa/checkpoints/2026-11-01/karnov-combat-nightly-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);q=json.loads((D/'handoff.json').read_text())
    assert q['passed']and q['installed']and not q['backup_created']and not q['complete']
    assert sha(Path(q['destination']))==sha(R/'build/karnov-host-resource-base-1101-v1/candidate.nes')==q['output_sha256']
    for k in ['source','native']:
        part=q[k];p=R/part['path'];assert sha(p)==part['sha256']
        with zipfile.ZipFile(p)as z:
            manifest=json.loads(z.read('files.json'));assert len(z.namelist())==part['members']
            for name,v in manifest.items():
                data=z.read(name);assert len(data)==v['bytes']and hashlib.sha256(data).hexdigest()==v['sha256']
    for v in q['components'].values():assert sha(R/v['path'])==v['sha256']
    for name in ['combat-crouch','block-row','final-menu']:
        c=R/'build/karnov-combat-native-1101-v7'/name
        ready=json.loads((c/'ready.json').read_text());validate(ready)
        result=json.loads((c/'capture/result.json').read_text());assert result['passed']and result['ROM_sha256']==q['output_sha256']
    readme=(R/'README.md').read_text(encoding='utf-8')
    assert 'Shots now damage enemies'in readme and 'karnov-combat-nightly-v7/README.md'in readme
    result=dict(passed=True,ROM_sha256=q['output_sha256'],installed_bytes_exact=True,
                source_native_and_component_archives_verified=True,README_UTF8_verified=True,
                finalization='The delivery generator completed installation and saved receipts before its final README read encountered Windows cp1252. README and current generator now use UTF-8. The frozen source/native packets and installed ROM were unchanged by this documentation repair.',
                storage=preflight(fresh=True),bindings={str(p.resolve()):sha(p)for p in [Path(__file__),D/'handoff.json',R/'README.md']})
    for p in [O/'result.json',D/'delivery-finalized.json']:p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
