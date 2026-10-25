"""One-shot adoption of the exact native-qualified no-op selection repair."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT='f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'
CANDIDATE='859b51acb503dde2b9f57ef45a6a6d2bc22a98aa726a331897ef0af6cc4ff587'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    proposal=D/'robots-weapon-audit-v1/proposal-v4'
    out=D/'robots-weapon-audit-v1/adoption-v1'
    assert not out.exists(),'One-shot adopter has already run; inspect retained state.'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(installed)==PARENT and sha(proposal/'candidate.nes')==CANDIDATE
    proofs=[D/p/'native-proof.json'for p in ['robots-native-v3-mega','robots-native-v3-proto','robots-native-v4-bass']]
    proofs += [proposal/p/'proof.json'for p in ['components-v1','transitions-v1']]
    for p in proofs:
        q=json.loads(p.read_text())
        assert q['passed']and q.get('ROM_sha256',q.get('candidate_ROM_sha256'))==CANDIDATE,p
    # Bind the accepted inputs to the proposal's full frozen source snapshot.
    # The two intentional source edits are checked against the original copies.
    original=D/'robots-weapon-audit-v1/proposal-v4/source'
    baseline=D/'zelda2-terrain-candidate-v4/source'
    expected_entry=(baseline/'src/entrypoint.s').read_bytes()
    assert (ROOT/'src/entrypoint.s').read_bytes()==expected_entry
    prepare=json.loads((proposal/'prepare.json').read_text())
    assert hashlib.sha256((ROOT/'src/inventory.s').read_text().encode()).hexdigest()==prepare['source_before_sha256']
    for top in ['src','inc','chr','audio','build/generated']:
        for p in (ROOT/top).rglob('*'):
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            if rel.as_posix()in ['src/entrypoint.s','src/inventory.s']:continue
            assert sha(p)==sha(original/rel),str(rel)
    for n in ['build_options.ini','smb1base-mmc5-expanded.cfg','smb1base.cfg']:
        assert sha(ROOT/n)==sha(original/n),n
    out.mkdir()
    shutil.copy2(installed,out/'previous-MMC5.nes')
    for n in ['entrypoint.s','inventory.s']:
        shutil.copy2(ROOT/'src'/n,out/('previous-'+n))
        shutil.copy2(original/'src'/n,ROOT/'src'/n)
    with(out/'fresh-build.log').open('w')as log:
        subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                        '--output',str(out/'candidate.nes')],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
    assert sha(out/'candidate.nes')==CANDIDATE,'Fresh root compile differs; do not install.'
    shutil.copy2(out/'candidate.nes',installed)
    assert sha(installed)==CANDIDATE
    receipt=dict(adopted=True,goal_complete=False,ROM_sha256=CANDIDATE,parent_ROM_sha256=PARENT,
                 fresh_root_compile_exact=True,installed_path=str(installed),
                 changed_ROM_bytes=30,changed_PRG_banks=[59],preexisting_exported_PC_RAM_CHR_exact=True,
                 proofs={str(p):sha(p)for p in proofs},backup_directory=str(out),
                 scope='No-op Mega/Proto/Bass weapon selection retains attacks/charge; actual transitions and non-robot cleanup unchanged. 548 CPU components,125 CPU transition cases,27 native UI cases/332 guarded NMIs. Explicit component staging, not full level/attack lifespan/PPU/audio or all-powerup qualification.')
    (out/'proof.json').write_text(json.dumps(receipt,indent=2)+'\n')
    dest=ROOT/'build/verification/robot-selection';dest.mkdir(exist_ok=True)
    shutil.copy2(out/'proof.json',dest/'proof.json')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
