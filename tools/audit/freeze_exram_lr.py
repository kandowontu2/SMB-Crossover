"""Freeze the expanded-profile RAM foundation, before adding new gameplay."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
O = R/'build/checkpoints/expanded-profiles-lr'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent=R/'build/checkpoints/protoman-ky'
    prior=json.loads((parent/'manifest.json').read_text())
    sources={
        'mmc3':R/'build/verification/third-row-lp/standard-mmc3/smb-crossover-mmc3.nes',
        'mmc5':R/'build/verification/third-row-lp/standard-check/smb-crossover-mmc5.nes',
        'mmc5-expanded':R/'build/verification/third-row-lp/smb-crossover-mmc5-exram.nes',
    }
    assert all(sha(sources[m])==prior['ROMs'][m] for m in ('mmc3','mmc5'))
    expected='3b90274e09eac19d8d12bd973c15b4a9ceedce0f742a21665d7f88683b32b0f3'
    assert sha(sources['mmc5-expanded'])==expected
    proof=R/'build/verification/smb-crossover-mmc5-exram-exram.json'
    native=R/'build/verification/smb-crossover-mmc5-exram-native-proto.json'
    assert json.loads(proof.read_text())['passed']
    assert json.loads(native.read_text())['passed']
    O.mkdir()
    with zipfile.ZipFile(parent/'source.zip') as z: names=set(z.namelist())
    names.update(('src/x5_profiles.s','tools/audit/x5_exram_native.lua','tools/audit/freeze_exram_lr.py'))
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(names): z.write(R/name,name)
    roms={}
    for mapper,source in sources.items():
        stem='smb-crossover-'+mapper
        for ext in ('.nes','.lbl','.dbg','.map'):
            sourcefile=source.with_suffix(ext)
            target=O/'build'/(stem+ext)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(sourcefile,target)
            if mapper=='mmc5-expanded': shutil.copyfile(sourcefile,R/'build'/(stem+ext))
        roms[mapper]=sha(source)
    report=dict(status='ADOPTED_EXPANDED_EXRAM_FOUNDATION_NEW_CHARACTERS_IN_PROGRESS',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        parent_checkpoint=str((parent/'manifest.json').relative_to(R)),ROMs=roms,
        source_files={n:sha(R/n) for n in sorted(names)},
        artifacts={p.relative_to(O).as_posix():sha(p) for p in O.rglob('*') if p.is_file()},
        native_proofs={str(p.relative_to(R)):sha(p) for p in (proof,native)},
        scope='MMC5 expanded-only CPU ExRAM state initialization. Current playable identities are unchanged; this checkpoint does not add Kirby/Darkwing/ZeldaII/Vic yet.',
        next_priority='New characters; user deferred videos/playthrough work.',goal_complete=False)
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=roms,source_count=len(names))))


if __name__=='__main__': main()
