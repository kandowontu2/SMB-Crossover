"""Adopt the exact combined native-qualified weapon admission fixes once."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT='49d980e564abfb8bfc71bf0c69d5f25c91afed0968d231f959252fa53552b174'
FINAL='55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proposal=D/'native-weapon-fixes-combined-v1';out=proposal/'adoption-v1'
    assert not out.exists(),'One-shot adopter already ran; inspect retained state.'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    alias=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert sha(installed)==sha(alias)==PARENT and sha(proposal/'candidate.nes')==FINAL
    build=json.loads((proposal/'build-proof.json').read_text())
    assert build['passed']and build['ROM_sha256']==FINAL and build['changed_bytes']==85
    proofs=[proposal/p/'native-proof.json'for p in ['native-10','native-11','native-smb3-0','native-smb3-1']]
    proofs.append(proposal/'cpu-smb3/proof.json')
    for p in proofs:
        q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==FINAL,p
    for mapper,expected in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                            ('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        assert sha(proposal/f'standard-{mapper}.nes')==expected
    for name,row in build['source_files'].items():
        p=ROOT/name
        assert (sha(p)if p.exists()else None)==row['before_sha256'],name
        assert sha(proposal/'source'/name)==row['after_sha256'],name
    out.mkdir();previous=out/'previous-source';previous.mkdir();missing=[]
    shutil.copy2(installed,out/'previous-MMC5.nes')
    oldalias=out/'previous-default';oldalias.mkdir()
    suffixes=['.nes','.dbg','.lbl','.map','.build.json','.build.log']
    for suffix in suffixes:
        p=alias.with_suffix(suffix)
        if p.exists():shutil.copy2(p,oldalias/p.name)
    for name in build['source_files']:
        p=ROOT/name
        if p.exists():
            dest=previous/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        else:missing.append(name)
    try:
        for name in build['source_files']:shutil.copy2(proposal/'source'/name,ROOT/name)
        with(out/'fresh-build.log').open('w')as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                            '--output',str(out/'candidate.nes')],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert sha(out/'candidate.nes')==FINAL,'Fresh root compile differs; restoring original sources.'
    except BaseException:
        for p in previous.rglob('*'):
            if p.is_file():shutil.copy2(p,ROOT/p.relative_to(previous))
        for name in missing:(ROOT/name).unlink()
        raise
    shutil.copy2(out/'candidate.nes',installed)
    for suffix in suffixes:shutil.copy2((out/'candidate.nes').with_suffix(suffix),alias.with_suffix(suffix))
    assert sha(installed)==sha(alias)==FINAL
    q=dict(adopted=True,goal_complete=False,ROM_sha256=FINAL,parent_ROM_sha256=PARENT,
           fresh_root_compile_exact=True,changed_PRG_banks=[6,37,90],changed_ROM_bytes=85,
           preexisting_exported_PC_RAM_and_CHR_exact=True,
           proofs={str(p):sha(p)for p in proofs},build_proof_sha256=sha(proposal/'build-proof.json'),
           backup_directory=str(out),Downloads_and_default_build_current=True,
           scope='Exact combined rerun:89 staged native cases,1248 CPU components, independent source hammer lifetime and original donor CPU/native proofs. Ryu grant during Slash, atomic Sophia triplet reservation, SMB3 Bowser and Buzzy weapon admission. Source35-hit boss balance remains adapted to host5HP. Standard mappers byte-exact. No natural all-item/full-level/campaign/audio/constant60Hz completion claim.')
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    target=ROOT/'build/verification/native-weapon-fixes';target.mkdir(exist_ok=True)
    shutil.copy2(out/'proof.json',target/'proof.json');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
