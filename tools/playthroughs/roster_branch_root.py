"""Bind an opaque discovery root to an independent controller-only replay."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def target_numbers(path):
    source = Path(path).read_text()
    return {key: int(re.search(r'\b' + key + r'=(\d+)', source)[1])
            for key in ('frame', 'poll')}


def bind_root(proof, basename, rom, verifier):
    """Call only after the fresh independent verifier has returned success."""
    proof = Path(proof)
    state = proof / (basename + '-verified-root.state')
    assert state.stat().st_size > 0, 'Verifier did not export an opaque root'
    metadata = dict(schema=1, verified_coldboot=True, savestate_loads=False,
                    emulated_writes=False, ram_bytes_identical=10240,
                    rom_sha256=sha(rom),
                    inputs_sha256=sha(proof / (basename + '-inputs.csv')),
                    target_sha256=sha(proof / (basename + '-target.lua')),
                    ram_sha256=sha(proof / (basename + '-ram.bin')),
                    state_sha256=sha(state), verifier_source_sha256=sha(verifier),
                    basename=basename, **target_numbers(proof / (basename + '-target.lua')))
    (proof / (basename + '-reusable-root.json')).write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata


def validate_root(proof, basename, rom, inputs, poll):
    proof = Path(proof).resolve()
    metadata = json.loads((proof / (basename + '-reusable-root.json')).read_text())
    manifest = json.loads((proof / 'manifest.json').read_text())
    assert manifest['branch_coldboot_verified' if basename == 'winning' else 'best_coldboot_verified'] is True, 'Proof has no independent cold-boot verification'
    assert manifest['emulated_memory_or_register_patches'] is False
    assert metadata['schema'] == 1 and metadata['basename'] == basename
    assert metadata['verified_coldboot'] is True and metadata['savestate_loads'] is False, 'Reusable root requires independent cold boot without state loads'
    assert metadata['emulated_writes'] is False and metadata['ram_bytes_identical'] == 10240, 'Reusable root verification permits no emulated writes'
    assert metadata['rom_sha256'] == sha(rom), 'Reusable root ROM differs'
    assert metadata['inputs_sha256'] == sha(inputs), 'Reusable root input stream differs'
    assert metadata['rom_sha256'] == manifest['rom_sha256']
    assert metadata['inputs_sha256'] == manifest[basename + '_inputs_sha256']
    assert any(core.exists() and sha(core) == metadata['verifier_source_sha256']
               for core in [proof / 'verify-core.lua', proof / (basename + '-root-verify-core.lua')]), 'Reusable root verifier source differs'
    for key, suffix in [('inputs', '-inputs.csv'), ('target', '-target.lua'),
                        ('ram', '-ram.bin'), ('state', '-verified-root.state')]:
        assert metadata[key + '_sha256'] == sha(proof / (basename + suffix)), 'Reusable root artifact differs: ' + key
    assert target_numbers(proof / (basename + '-target.lua')) == {k: metadata[k] for k in ('frame', 'poll')}
    assert poll == metadata['poll'], 'Reusable root poll differs'
    return metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('proof', type=Path)
    p.add_argument('--basename', choices=('winning', 'best'), default='winning')
    p.add_argument('--timeout', type=int, default=360)
    a = p.parse_args()
    proof = a.proof.resolve()
    manifest = json.loads((proof / 'manifest.json').read_text())
    assert manifest['branch_coldboot_verified' if a.basename == 'winning' else 'best_coldboot_verified'] is True
    assert manifest['emulated_memory_or_register_patches'] is False
    roms = list(proof.glob('*.nes'))
    assert len(roms) == 1
    rom = roms[0]
    inputs = proof / (a.basename + '-inputs.csv')
    assert sha(rom) == manifest['rom_sha256']
    assert sha(inputs) == manifest[a.basename + '_inputs_sha256']
    if (proof / (a.basename + '-reusable-root.json')).exists():
        metadata = validate_root(proof, a.basename, rom, inputs,
                                 target_numbers(proof / (a.basename + '-target.lua'))['poll'])
        print(json.dumps(metadata, indent=2))
        return 0
    core = proof / (a.basename + '-root-verify-core.lua')
    shutil.copyfile(ROOT / 'tools/playthroughs/roster_branch_verify.lua', core)
    script = proof / (a.basename + '-prepare-root-' + proof.name + '-' + str(time.time_ns()) + '.lua')
    script.write_text('BRANCH_VERIFY={out=' + json.dumps(proof.as_posix() + '/') +
                      ',basename=' + json.dumps(a.basename) + ',exportRoot=true}\n' +
                      'dofile(' + json.dumps(core.as_posix()) + ')\n')
    result = run_mesen.run(script, rom, timeout=a.timeout, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false'])
    log = ROOT / 'build/verification' / (rom.stem + '-' + script.stem + '.log')
    if log.exists():
        shutil.copyfile(log, proof / (script.stem + '.log'))
    if result:
        return result
    print(json.dumps(bind_root(proof, a.basename, rom, core), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
