"""Adopt the reviewed LR-based Darkwing packet and preserve its baseline."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
D = R/'build/player-guide-agent/darkwing-private'
O = R/'build/verification/darkwing-adoption-lz'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists(), 'Use a fresh adoption identifier'
    manifest = json.loads((D/'candidate-manifest.json').read_text())
    assert manifest['baseline_rom_sha256'] == sha(R/'build/smb-crossover-mmc5-expanded.nes')
    assert manifest['rom_sha256'] == sha(D/'darkwing-candidate.nes')
    with zipfile.ZipFile(R/'build/checkpoints/expanded-profiles-lr/source.zip') as z:
        baseline = {n:z.read(n) for n in z.namelist()}
    changed = ['src/'+n for n in manifest['modified_hooks']]
    changed.append('smb1base-mmc5-expanded.cfg')
    added = ['src/'+n for n in ('darkwing.s','darkwing_core.s','darkwing_weapons.s',
                               'darkwing_pickups.s','darkwing_recovery.s','darkwing_art.inc')]
    added.append('chr/characters/darkwing.chr')
    # Verify every input before mutating the main source.
    for name in changed:
        assert (R/name).read_bytes() == baseline[name], name
        assert (D/'source'/name).is_file(), name
        if name.startswith('src/'):
            assert sha(D/'source'/name)==manifest['modified_hooks'][Path(name).name]['sha256']
    for name in added:
        assert not (R/name).exists(), name
    before = {n:sha(R/n) for n in changed}
    O.mkdir(parents=True)
    for name in changed:
        dest = O/'before'/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(R/name,dest)
        shutil.copyfile(D/'source'/name,R/name)
    for name in added[:-1]:
        shutil.copyfile(D/'source'/name,R/name)
    shutil.copyfile(D/'art/darkwing.chr',R/added[-1])
    entry = R/'src/darkwing.s'
    text = entry.read_text()
    old = (D/'art/darkwing.chr').as_posix()
    assert text.count(old) == 1
    entry.write_text(text.replace(old,'chr/characters/darkwing.chr'))
    report = dict(status='SOURCE_ADOPTED_PENDING_MAIN_BUILD',
        packet_sha256=sha(D/'candidate-manifest.json'),
        expected_expanded_rom_sha256=manifest['rom_sha256'],
        before=before, after={n:sha(R/n) for n in changed+added},
        scope='Darkwing alternate for Scrooge; original motion/art/three gas adaptors; native SMB Arrow recovery pickup.',
        limitations=['Music currently uses the Scrooge driver and SMB cues.'],
        goal_complete=False)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
