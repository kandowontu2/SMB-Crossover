"""Adopt the exact qualified platform/body and late native-girder composition."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT='859b51acb503dde2b9f57ef45a6a6d2bc22a98aa726a331897ef0af6cc4ff587'
FINAL='49d980e564abfb8bfc71bf0c69d5f25c91afed0968d231f959252fa53552b174'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    candidate=D/'zelda2-platform-late-candidate-v4'
    source=candidate/'source';out=candidate/'adoption-v1'
    assert not out.exists(),'One-shot adopter already ran; inspect retained state.'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(installed)==PARENT and sha(candidate/'candidate.nes')==FINAL
    proofs=[D/p for p in [
        'zelda2-platform-late-candidate-v3/cpu-proof.json',
        'zelda2-platform-late-candidate-v3/ground-cpu-proof.json',
        'zelda2-platform-late-candidate-v3/balance-cpu-proof.json',
        'zelda2-platform-late-candidate-v3/late-cpu-proof.json',
        'zelda2-platform-native-late-v3-arena1/native-proof.json',
        'zelda2-platform-balance-late-v3-native2/native-proof.json',
        'zelda2-platform-late-v3-routes-v1/proof.json']]
    for p in proofs:
        q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==FINAL,p
    # Conditional legacy names were restored without changing expanded bytes.
    for mapper,expected in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                            ('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        assert sha(candidate/f'standard-{mapper}.nes')==expected
    files=[p for p in source.rglob('*')if p.is_file()]
    assert all(p.relative_to(source).parts[0]=='src'or p.name=='smb1base-mmc5-expanded.cfg'for p in files)
    assert len(files)==14,len(files)
    out.mkdir();shutil.copy2(installed,out/'previous-MMC5.nes')
    previous=out/'previous-source';previous.mkdir();missing=[]
    for p in files:
        rel=p.relative_to(source);dest=ROOT/rel
        assert dest.resolve().is_relative_to(ROOT)
        if dest.exists():
            backup=previous/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup)
        else:missing.append(rel.as_posix())
    (out/'missing-before.json').write_text(json.dumps(missing,indent=2)+'\n')
    try:
        for p in files:shutil.copy2(p,ROOT/p.relative_to(source))
        with(out/'fresh-build.log').open('w')as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                            '--output',str(out/'candidate.nes')],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert sha(out/'candidate.nes')==FINAL,'Fresh root compile differs; restoring original source.'
    except BaseException:
        for p in previous.rglob('*'):
            if p.is_file():shutil.copy2(p,ROOT/p.relative_to(previous))
        for n in missing:(ROOT/n).unlink()
        raise
    shutil.copy2(out/'candidate.nes',installed);assert sha(installed)==FINAL
    q=dict(adopted=True,goal_complete=False,ROM_sha256=FINAL,parent_ROM_sha256=PARENT,
           fresh_root_compile_exact=True,installed_path=str(installed),existing_RAM_and_CHR_exact=True,
           source={str(p.relative_to(source)):sha(p)for p in files},
           proofs={str(p):sha(p)for p in proofs},backup_directory=str(out),
           scope='Zelda II original standing/crouched body projection, private platform envelope/Fairy26px feet, actual native paired support origins; native small-lift guest sprites survive OAM rotation. 58 staged native arenas plus zero-death Easy4751/Hard4840 controller-only1-1 discoveries and CPU oracles. Original native actors, geometry, movement and carry reused. No new independent full-route PPU/audio or whole-roster/campaign/constant60Hz admission.')
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    target=ROOT/'build/verification/zelda2-platform';target.mkdir(exist_ok=True)
    shutil.copy2(out/'proof.json',target/'proof.json');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
