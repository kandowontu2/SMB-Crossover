"""Merge an immutable reviewed TMNT packet onto NX outside the live workspace."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-review-ny')
OWNED = {
    'src/tmnt.s', 'src/tmnt_animation.inc', 'src/tmnt_art.inc',
    'src/tmnt_combat.s', 'src/tmnt_core.s', 'src/tmnt_dispatch.s',
    'src/tmnt_draw.s', 'src/tmnt_equipment.s', 'src/tmnt_equipment_draw.s',
    'src/tmnt_native_motion.s', 'src/tmnt_projectiles.s',
    'src/tmnt_secondary_art.inc', 'src/tmnt_state.inc',
    'src/roll_dispatch.s', 'src/vic_dispatch.s',
    'src/smb3_mario_pickups.s', 'src/little_mac_combat.s',
    'chr/characters/tmnt.chr',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(path, destination):
    destination.mkdir(exist_ok=False)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert all((destination / n).resolve().is_relative_to(destination.resolve())
                   for n in z.namelist())
        z.extractall(destination)
        return {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--agent-rom', type=Path, required=True)
    p.add_argument('--agent-sha', required=True)
    p.add_argument('--label', required=True)
    a = p.parse_args()
    assert a.label and all(c.isalnum() or c in '-_' for c in a.label)
    assert sha(a.agent_rom) == a.agent_sha
    out = OUT / a.label
    out.mkdir(exist_ok=False)
    nx = ROOT / 'build/checkpoints/mike-source-art-nx'
    nw = ROOT / 'build/checkpoints/vic-hud-font-nw'
    parent = json.loads((nx / 'manifest.json').read_text())
    assert parent['rom_sha256'] == sha(nx / 'candidate.nes')
    source = out / 'source'
    unpack(nx / 'source.zip', source)
    assert all(sha(source / n) == h for n, h in parent['source_files'].items())
    packet = unpack(a.packet, out / 'packet')
    assert set(packet) == OWNED
    changes = {}
    for n, h in packet.items():
        before = sha(source / n) if (source / n).exists() else None
        if before != h:
            changes[n] = {'before': before, 'after': h}
        (source / n).write_bytes((out / 'packet' / n).read_bytes())
    rom = out / 'candidate.nes'
    result = subprocess.run([
        sys.executable, str(source / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(source), '--compiler',
        str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(rom)
    ], cwd=source, capture_output=True, text=True)
    (out / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    # Independently compose the disjoint byte changes. No byte changed by the
    # agent may erase NX's already accepted source-art/HUD repair.
    original = (nw / 'candidate.nes').read_bytes()
    nx_rom = (nx / 'candidate.nes').read_bytes()
    agent = a.agent_rom.read_bytes()
    actual = rom.read_bytes()
    assert len(original) == len(nx_rom) == len(agent) == len(actual)
    composed = bytearray(nx_rom)
    conflicts = []
    count = 0
    for i, (old, new) in enumerate(zip(original, agent)):
        if old == new:
            continue
        count += 1
        if nx_rom[i] != old and nx_rom[i] != new:
            conflicts.append(i)
        composed[i] = new
    assert not conflicts, conflicts[:32]
    assert actual == composed, 'Source merge differs from independent byte composition'
    report = dict(passed=True, ROM_sha256=sha(rom), parent_ROM_sha256=sha(nx / 'candidate.nes'),
                  agent_ROM_sha256=a.agent_sha, agent_packet_sha256=sha(a.packet),
                  packet_files=packet, source_changes=changes,
                  agent_changed_bytes=count, disjoint_byte_composition_exact=True,
                  source_parent_files_verified=len(parent['source_files']),
                  scope='Private staged source merge only; native integration acceptance pending.')
    (out / 'source-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
