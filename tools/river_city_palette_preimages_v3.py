"""Prepare13 sparse preimages for the independent RCR palette test build.

Run before river_city_palette_private_build_v3.py on a fresh workspace. This
recovers only the files owned by concurrent Celeste integration, using the
already-pushed root revision; no repository checkout/reset or tree copy.
"""
from pathlib import Path
import hashlib
import json
import subprocess

R = Path(__file__).resolve().parents[1]
FILES = [
    'src/entrypoint.s','smb1base-mmc5-expanded.cfg','src/samus.s',
    'src/megaman_weapons.s','src/new_roster_dispatch.s','src/player.s',
    'src/megaman_physics.s','src/megaman_environment.s','src/object.s',
    'src/character_select.s','src/collision.s','src/x5_bounce.s','src/cheats_four.s']


def main():
    overlay = R/'build/river-city-palette-runtime-v3-overlay'
    overlay.mkdir(exist_ok=False)
    bindings = []
    for name in FILES:
        command = ['git','show','1a80fc9c:'+name]
        result = subprocess.run(command,cwd=R,capture_output=True)
        assert result.returncode == 0, result.stderr
        path = overlay/name
        path.parent.mkdir(exist_ok=True,parents=True)
        path.write_bytes(result.stdout)
        bindings.append(dict(path=name,sha256=hashlib.sha256(result.stdout).hexdigest()))
    (overlay/'snapshot.json').write_text(json.dumps(dict(preimages=FILES,
          source_commit='1a80fc9c',bindings=bindings,canonical_unchanged=True),indent=2)+'\n')
    command = ['python','-B','tools/build_mmc5_expanded.py','--source-overlay',str(overlay),
               '--output','build/river-city-palette-baseline-v3.nes']
    result = subprocess.run(command,cwd=R,capture_output=True,text=True)
    assert result.returncode == 0, result.stdout+result.stderr
    baseline = R/'build/river-city-palette-baseline-v3.nes'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() == '33d2c7a7bf58aa040f2911d44f1d59dddb4c9b40b3e8727334cf46db74915f97'
    print('Exact33d2 baseline; now run river_city_palette_private_build_v3.py')


if __name__ == '__main__':
    main()
