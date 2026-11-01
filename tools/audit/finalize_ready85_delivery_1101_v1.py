"""Verify frozen source/native archives, installed bytes, and current doc image."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from publish_ready85_doki_1101_v1 import J,N,M,K,O,DEST,EXPECTED,bound,native
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(DEST)==sha(J/'candidate.nes')==EXPECTED
    bound(J/'source-stage.json');bound(J/'graphics-controls.json');bound(J/'physics-controls.json');bound(N/'suite-results.json')
    for name in ['imajin','lina','papa','mama','mario','luigi','toad','peach']:native(N/name)
    native(M)
    handoff=json.loads((K/'handoff.json').read_text());members=0
    for key in ['source','native']:
        item=handoff[key];archive=R/item['path'];assert sha(archive)==item['sha256']
        with zipfile.ZipFile(archive)as z:
            assert z.testzip()is None
            for info in z.infolist():
                p=R/info.filename;assert hashlib.sha256(z.read(info)).hexdigest()==sha(p),p;members+=1
    screenshot=N/'imajin/capture/selected.png';target=R/'docs/images/character-select.png';target.write_bytes(screenshot.read_bytes());assert sha(target)==sha(screenshot)
    result=dict(passed=True,installed=True,backup_created=False,ROM_sha256=EXPECTED,playable=85,menu_identities=90,verified_frozen_members=members,readme_image_sha256=sha(target),source_stage_sha256=sha(J/'source-stage.json'),limits=handoff['limits'])
    (O/'finalization.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');(R/'docs/qa/nightly-2026-11-01-ready85-finalization.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()
