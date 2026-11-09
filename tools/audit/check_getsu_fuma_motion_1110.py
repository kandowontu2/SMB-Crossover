"""Compare Getsu Fūma's linked movement and basic sword to the donor."""

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess
import tempfile

from py65.devices.mpu6502 import MPU

from trace_getsu_fuma_donor_1110 import PIN, ROM, ROOT, digest


SOURCE = ROOT / 'tools/reference/getsu_fuma_motion_1110.s'
SWORD = ROOT / 'tools/reference/getsu_fuma_sword_1110.s'
CAPTURE = ROOT / 'build/getsu-fuma-donor-action-1110/capture'
BASE = 0x5800
STOP = 0x5b00
NAMES = ('Action Facing VXLo VXHi VYLo VYHi YLo YHi JumpHold Support Pad Sign '
         'Clock BodyPose BodyFacing SwordActive SwordPhase SwordPose SwordFacing SwordCue').split()
LOCAL = {name: 0x6100 + i for i, name in enumerate(NAMES)}
DONOR = dict(Action=0x4f, Facing=0x1c4, VXLo=0x3f0, VXHi=0x3f8,
             VYLo=0x3e0, VYHi=0x3e8, YLo=0x320, YHi=0x340, JumpHold=0x5b,
             Support=0x5e, Pad=0xf0, Sign=0x07, Clock=0xe1, BodyPose=0x300,
             BodyFacing=0x3c0, SwordActive=0x54, SwordPhase=0x52, SwordPose=0x301,
             SwordFacing=0x3c1)


def assemble(output):
    with tempfile.TemporaryDirectory(prefix='link-', dir=output) as folder:
        out = Path(folder)
        src, obj, cfg, binary, labels = (out / f'motion.{ext}' for ext in ('s', 'o', 'cfg', 'bin', 'lbl'))
        defs = ''.join(f'Gf{name}=${address:04x}\n' for name, address in LOCAL.items())
        assembly = SOURCE.read_text() + '\n' + SWORD.read_text()
        src.write_text(defs + re.sub(r'^\.import .+\n', '', assembly, flags=re.M))
        cfg.write_text('MEMORY { M:start=$5800,size=$200,file=%O; } '
                       'SEGMENTS { GETSU_MOTION:load=M,type=ro; GETSU_SWORD:load=M,type=ro; }\n')
        cc = ROOT / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', src, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        symbols = {line.split()[2][1:]: int(line.split()[1], 16) for line in labels.read_text().splitlines()}
        return binary.read_bytes(), symbols


def execute(cpu, entry, state, addresses, outputs, cuts=(STOP,), cues=None):
    for name, value in state.items():
        cpu.memory[addresses[name]] = value
    cpu.pc, cpu.a, cpu.p, cpu.sp = entry, state.get('Pad', 0), 0x31, 0xfd
    cpu.stPushWord(STOP - 1)
    for _ in range(100):
        if cpu.pc in cuts:
            assert cpu.sp == (0xfd if cpu.pc == STOP else 0xfb)
            return tuple(cpu.memory[addresses[name]] for name in outputs)
        if cpu.pc == 0xc35f and cues is not None:
            cues.append(cpu.a)
            cpu.pc = (cpu.stPopWord() + 1) & 0xffff
            continue
        assert cpu.memory[cpu.pc] != 0, hex(cpu.pc)
        cpu.step()
    raise AssertionError(('nonreturning kernel', hex(entry), hex(cpu.pc)))


def compare(raw, code, symbols):
    original, linked = MPU(), MPU()
    original.memory[0xc000:] = raw[16 + 14 * 8192:16 + 16 * 8192]
    linked.memory[BASE:BASE + len(code)] = code
    original.memory[0x50] = 1  # Basic sword equipment selected in the live trace.

    def pair(name, pc, inputs, outputs, cuts=(STOP,)):
        expected = execute(original, pc, inputs, DONOR, outputs, cuts)
        actual = execute(linked, symbols['Gf' + name], inputs, LOCAL, outputs)
        assert actual == expected, (name, inputs, actual, expected)
        return actual

    horizontal = 0
    for velocity, pad, action, facing in itertools.product(range(-768, 769, 32), range(4), range(4), range(2)):
        fields = dict(VXLo=velocity & 255, VXHi=(velocity >> 8) & 255, Pad=pad,
                      Action=action, Facing=facing)
        pair('HorizontalSpeed', 0xeb0b, fields, ('VXLo', 'VXHi', 'Facing'), (0xeb2c, 0xeb9e, STOP))
        horizontal += 1

    jump = pair('JumpStart', 0xe336, dict(Action=0xff, VYLo=0xff, VYHi=0xff, JumpHold=32, Support=1),
                ('Action', 'VYLo', 'VYHi', 'JumpHold', 'Support'), (0xe34a,))
    assert jump == (2, 0x80, 0xfd, 0, 0)

    vertical = 0
    for velocity, pad, hold in itertools.product(range(-1024, 1025, 64), (0, 128), (0, 1, 20, 21, 22, 23, 255)):
        fields = dict(VYLo=velocity & 255, VYHi=(velocity >> 8) & 255, Pad=pad, JumpHold=hold)
        pair('VerticalSpeed', 0xe542, fields, ('VYLo', 'VYHi', 'JumpHold'), (0xe572,))
        vertical += 1

    positions = 0
    for y, velocity in itertools.product((0, 1, 255, 256, 0x3fff, 0xc800, 0xffff), range(-1024, 1025, 64)):
        fields = dict(YLo=y & 255, YHi=y >> 8, VYLo=velocity & 255, VYHi=(velocity >> 8) & 255)
        pair('IntegrateY', 0xecf5, fields, ('YLo', 'YHi'))
        positions += 1
    sword_starts = 0
    for active, phase in itertools.product((0, 1), range(6)):
        pair('SwordStart', 0xe366, dict(SwordActive=active, SwordPhase=phase), ('SwordActive', 'SwordPhase'))
        sword_starts += 1

    sword_updates = cue_updates = 0
    output = ('Action', 'BodyPose', 'BodyFacing', 'SwordActive', 'SwordPhase', 'SwordPose', 'SwordFacing')
    for active, phase, clock, action, facing, speed in itertools.product(
            (0, 1), range(6), range(4), range(16), (0, 1), (0, 0x180, -0x180)):
        fields = dict(Action=action, Facing=facing, VXLo=speed & 255, VXHi=(speed >> 8) & 255,
                      Clock=clock, BodyPose=0x55, BodyFacing=facing ^ 1, SwordActive=active,
                      SwordPhase=phase, SwordPose=0x33, SwordFacing=facing ^ 1)
        cues = []
        expected = execute(original, 0xe62a, fields, DONOR, output, cues=cues)
        assert cues in ([], [0x25])
        actual = execute(linked, symbols['GfSwordAdvance'], fields, LOCAL, (*output, 'SwordCue'))
        assert actual == (*expected, cues[0] if cues else 0), (fields, actual, expected, cues)
        sword_updates += 1
        cue_updates += bool(cues)
    return dict(horizontal=horizontal, jump_entry=1, vertical_speed=vertical, vertical_position=positions,
                sword_starts=sword_starts, sword_updates=sword_updates, sword_cue_updates=cue_updates)


def check_native_trace(raw):
    samples = json.loads((CAPTURE / 'observations.json').read_text())['checkpoints']
    marks = {s['name']: s for s in samples}
    assert marks['zone-entry']['frame'] == 4044
    assert all(s['dma_prg'] == 115261 and s['ppu_control'] & 0x20 for s in samples)
    assert len({s['sprite_palette'] for s in samples}) == 1
    for name, wanted in {'idle': (169, 8, 118), 'walk': (185, 40, 118),
                         'jump': (121, 4, 118), 'sword': (153, 92, 126),
                         'crouch': (193, 48, 118), 'crouch-sword': (161, 92, 126)}.items():
        assert any((y, tile, x) == wanted for _, y, tile, _, x in marks[name]['oam']), name
    chr_rom = raw[16 + 8 * 16384:]
    body_tiles = {}
    for name in ('idle', 'walk', 'jump', 'sword', 'crouch', 'crouch-sword'):
        sample = marks[name]
        patterns = {tile: bytes.fromhex(p) for tile, _, p in sample['visible_patterns']}
        rows = []
        for _, y, tile, flags, x in sample['oam']:
            if 118 <= x <= 134 and 100 <= y < 200:
                pattern = patterns[tile]
                offsets = [off for off in range(0, len(chr_rom) - 31, 16) if chr_rom[off:off + 32] == pattern]
                assert offsets, (name, tile)
                rows.append(dict(y=y, x=x, tile=tile, attributes=flags, donor_CHR_offsets=offsets))
        body_tiles[name] = rows
    with (CAPTURE / 'writers.csv').open() as file:
        writers = list(csv.DictReader(file))
    signatures = {(row['phase'], row['after_pc'], row['ram']) for row in writers}
    assert {('walk', 'ed1b', '03f0'), ('jump', 'e56a', '03e0'), ('jump', 'ed08', '0340'),
            ('sword', 'e376', '0054'), ('sword', 'e639', '0052'), ('crouch', 'e29e', '0341')} <= signatures
    return dict(stage='first original action zone', controller_only=True,
                sprite_palette=marks['idle']['sprite_palette'], pose_tiles=body_tiles,
                sword_phase_table=raw[16 + 15 * 8192 + 0xedf:16 + 15 * 8192 + 0xee5].hex(),
                observed_writer_signatures=len(signatures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert digest(ROM) == PIN
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'build')
    output.mkdir(exist_ok=True)
    code, symbols = assemble(output)
    raw = ROM.read_bytes()
    cpu = compare(raw, code, symbols)
    trace = check_native_trace(raw)
    inputs = (Path(__file__), SOURCE, SWORD, CAPTURE / 'observations.json', CAPTURE / 'writers.csv')
    bindings = {str(f): digest(f) for f in inputs}
    result = dict(passed=True, donor_SHA256=PIN, source_component_bytes=len(code),
                  source_component_SHA256=hashlib.sha256(code).hexdigest(), linked_CPU=cpu,
                  native_donor=trace, resident_host=False, bindings=bindings)
    (output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, bytes=len(code), cases=cpu)))


if __name__ == '__main__':
    main()
