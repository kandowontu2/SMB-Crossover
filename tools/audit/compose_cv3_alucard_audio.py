"""Compose the qualified original Alucard noise cue onto accepted Samus84."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328'
DONOR = '3868907c79cb1db9c6443052c79ba220706b61641946dce030f5bd65da47d4ce'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    donor = D / 'cv3-primary-sfx-v1/alucard-wrapper-v7'
    parent = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    assert sha(parent) == PARENT and sha(donor / 'candidate.nes') == DONOR
    binding = json.loads((donor / 'source-final.json').read_text())
    assert binding['passed'] and binding['producer_output_exact']
    for name, expected in binding['source_files'].items():
        assert sha(donor / 'source' / name) == expected, name
    source = out / 'source'
    shutil.copytree(D / 'samus-wave-combined220-v1/source', source)
    # Canonical accepted source text, including restored original line endings.
    for directory in ['src', 'inc', 'audio', 'chr']:
        shutil.copytree(ROOT / directory, source / directory, dirs_exist_ok=True)
    files = {}
    for name in binding['source_files']:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        before = sha(ROOT / name) if (ROOT / name).exists() else None
        if name == 'src/entrypoint.s':
            raw = (ROOT / name).read_bytes()
            assert b'cv3_source_audio.s' not in raw
            eol = b'\r\n' if b'\r\n' in raw else b'\n'
            addition = '\n.if ::ENABLE_MMC5_EXPANDED\n.include "cv3_source_audio.s"\n.endif\n'
            target.write_bytes(raw + addition.replace('\n', eol.decode()).encode())
        else:
            shutil.copy2(donor / 'source' / name, target)
        files[name] = dict(before_sha256=before, after_sha256=sha(target))
    provenance = source / 'docs/reference/metroid-apu-stores.json'
    provenance.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'docs/reference/metroid-apu-stores.json', provenance)
    generated = source / 'build/generated/guest-audio'
    generated_before = {str(p.relative_to(generated)): sha(p) for p in generated.rglob('*') if p.is_file()}
    with (out / 'producer.log').open('w') as log:
        subprocess.run([sys.executable, str(source / 'tools/prepare_guest_audio.py')],
                       cwd=source, stdout=log, stderr=subprocess.STDOUT, check=True)
    generated_after = {str(p.relative_to(generated)): sha(p) for p in generated.rglob('*') if p.is_file()}
    assert generated_before == generated_after, 'Producer changed the frozen generated assets'
    command = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe')]
    target = out / 'candidate.nes'
    with (out / 'host-build.log').open('w') as log:
        subprocess.run(command + ['--output', str(target)], cwd=ROOT, check=True,
                       stdout=log, stderr=subprocess.STDOUT)
    old, raw, repair = parent.read_bytes(), target.read_bytes(), (donor / 'candidate.nes').read_bytes()
    assert old[:16] == raw[:16] and old[16+1048576:] == raw[16+1048576:]
    banks = [27, 28, 82, 84]
    for bank in range(128):
        span = slice(16+bank*8192, 16+(bank+1)*8192)
        assert raw[span] == (repair if bank in banks else old)[span], bank
    before, after = qualified(parent), qualified(target)
    # The unrolled replacement intentionally removes the old restore loop's
    # private back-edge label. Its numeric address is now a JSR operand, so
    # inventing a compatibility entry there would mislead debugger clients.
    removed = {name: value for name, value in before.items() if after.get(name) != value}
    expected_removed = {('LOCAL-MACRO_SYMBOL-14BD', 'Load'): 0xdce9}
    assert removed == expected_removed, removed
    assert ('LOCAL-MACRO_SYMBOL-14BD', 'Load') not in after
    pos = 16+28*8192+0x1ce7
    assert old[pos:pos+3] == bytes.fromhex('a017be')
    assert old[pos+15:pos+20] == bytes.fromhex('88c0ffd0ee')
    assert raw[pos] == 0x20 and raw[pos+3] == 0x4c and raw[pos+6:pos+20] == bytes([0xea])*14
    for suffix in ['.nes', '.dbg', '.lbl', '.map']:
        shutil.copy2(parent.with_suffix(suffix), out / ('baseline' + suffix))
    ordinary = {}
    for mapper, expected in [
        ('mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
        ('mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        path = out / ('standard-' + mapper + '.nes')
        with (out / ('standard-' + mapper + '-host.log')).open('w') as log:
            subprocess.run(command + ['--flag-off', mapper, '--output', str(path)], cwd=ROOT,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        ordinary[mapper] = sha(path)
        assert ordinary[mapper] == expected
    proof = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=sha(target),
                 parent_ROM_sha256=PARENT, donor_ROM_sha256=DONOR, changed_PRG_banks=banks,
                 changed_bytes=sum(x != y for x, y in zip(old, raw)),
                 retained_qualified_addresses_exact=True, qualified_symbols=len(before),
                 intentionally_removed_private_labels=[dict(scope=name[0], name=name[1], old_address=value)
                                                       for name, value in removed.items()],
                 all_other_ROM_bytes_parent_exact=True, CHR_exact=True, new_RAM_bytes=0,
                 source_files=files, producer_all_generated_outputs_exact=True,
                 generated_outputs=generated_after, ordinary_target_hashes=ordinary,
                 scope='Complete-bank composition and fresh durable producer/build controls. Current-hash native and CPU tests required before adoption.')
    (out / 'build-proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in proof.items() if k not in ['source_files', 'generated_outputs']}, indent=2))


if __name__ == '__main__':
    main()
