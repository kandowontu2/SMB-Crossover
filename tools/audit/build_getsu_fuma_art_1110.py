"""Recover Getsu Fūma's basic-sword art from the original OAM renderer."""

import argparse
from collections import Counter
import csv
import itertools
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU

from trace_getsu_fuma_donor_1110 import PIN, ROM, ROOT, digest


CAPTURE = ROOT / 'build/getsu-fuma-donor-action-1110/capture'
INPUTS = {
    CAPTURE / 'observations.json': 'fb68ce7b1235da23bf0a82d2bcc5dd4ab13936963a901b71a2aa964c78bae70c',
    CAPTURE / 'writers.csv': 'f6642244b82ad098fbdd48686bb93ec45c557b5080940d19851e9bad07216058',
    ROOT / 'build/getsu-fuma-kernels-1110/proof.json': '00e2f32ae61066e0624e0753326d28bff3f776e5bdd2db5fbfd9396b161b86fc',
}
PRG_SIZE = 0x20000
ENTRY = 0x807a
TABLE = 0x81c2
STOP = 0x5b00
RIGHT, LEFT = 0, 1
ANCHOR_X, ANCHOR_Y = 128, 200


def fixed(raw, address, size=1):
    start = 16 + 0x1c000 + address - 0xc000
    return raw[start:start + size]


def source_poses(raw):
    walk_body = fixed(raw, 0xeecd, 4)
    walk_upper = fixed(raw, 0xeed1, 4)
    idle, crouch, head = fixed(raw, 0xeedb, 3)
    sword = fixed(raw, 0xeedf, 6)
    assert (walk_body, walk_upper, idle, crouch, head, sword) == (
        b'\x04\x05\x06\x05', b'\x01\x02\x03\x02', 12, 22, 37, b'\x01\x07\x08\x09\x0a\x0b')
    assert fixed(raw, 0xe098, 10) == bytes.fromhex('a9038d0103a90c8d0003')
    assert fixed(raw, 0xe295, 10) == bytes.fromhex('ad40031869088d410360')
    return dict(walk_body=list(walk_body), walk_upper=list(walk_upper), idle=idle,
                crouch=crouch, head_contact=head, sword=list(sword), initial_upper=3)


def oam_slots(start):
    for _ in range(63):
        yield start
        start = (start + 33) & 63
        if start == 0:
            start = 33


class DonorOam:
    def __init__(self, raw):
        self.cpu = MPU()
        self.cpu.memory[0x8000:0xc000] = raw[16 + 0x14000:16 + 0x18000]
        self.cpu.memory[0xc000:] = fixed(raw, 0xc000, 0x4000)
        assert self.cpu.memory[0x8082:0x8095] == list(bytes.fromhex(
            'a5f7c901f00dbdc2818502bdc38185034cbc80'))

    def record(self, pose):
        mem = self.cpu.memory
        return mem[TABLE + pose * 2] | (mem[TABLE + pose * 2 + 1] << 8)

    def render(self, layers, start):
        """Layers are (actor slot, pose, source facing, anchor X, anchor Y)."""
        cpu, mem = self.cpu, self.cpu.memory
        mem[0x200:0x300] = [0xf4] * 256
        mem[0], mem[0xe4], mem[0xf7] = 62, start * 4, 0
        for actor, pose, face, x, y in layers:
            mem[0x340 + actor], mem[0x380 + actor], mem[0x3c0 + actor] = y, x, face
            mem[0x3a0 + actor] = 0
            cpu.pc, cpu.a, cpu.y, cpu.p, cpu.sp = ENTRY, pose, actor, 0x30, 0xfd
            cpu.stPushWord(STOP - 1)
            for _ in range(400):
                if cpu.pc == STOP:
                    break
                assert 0x806f <= cpu.pc < TABLE, (pose, hex(cpu.pc))
                cpu.step()
            else:
                raise AssertionError(('nonreturning donor renderer', pose, hex(cpu.pc)))
            assert cpu.sp == 0xfd
        return [(slot, *mem[0x200 + slot * 4:0x204 + slot * 4])
                for slot in itertools.islice(oam_slots(start), 62 - mem[0])]


def encode(donor, poses):
    records = {}
    for actor, pose in poses:
        rows = donor.render([(actor, pose, RIGHT, ANCHOR_X, ANCHOR_Y)], 1)
        records[pose] = [(x - ANCHOR_X, y - ANCHOR_Y, tile, attr)
                         for _, y, tile, attr, x in rows]
    tiles = sorted({tile for row in records.values() for _, _, tile, _ in row})
    assert len(tiles) <= 32 and all(tile % 2 == 0 for tile in tiles)
    assert all(attr in (0, 0x40) for row in records.values() for _, _, _, attr in row)
    tile_map = {tile: index * 2 for index, tile in enumerate(tiles)}
    offsets, data = bytearray([0xff] * (1 + max(records))), bytearray()
    for pose, row in sorted(records.items()):
        assert len(data) < 0xff
        offsets[pose] = len(data)
        data.append(len(row))
        for dx, dy, tile, attr in row:
            data.extend((dx & 255, dy & 255, tile_map[tile] | attr << 1))
    return bytes(offsets), bytes(data), tiles


def signed(byte):
    return byte if byte < 128 else byte - 256


def decode(offsets, data, layers, start):
    slots, oam = oam_slots(start), []
    for _, pose, face, x, y in layers:
        if pose >= len(offsets) or offsets[pose] == 0xff:
            continue
        offset = offsets[pose]
        row = data[offset + 1:offset + 1 + 3 * data[offset]]
        for dx, dy, flags_tile in zip(row[::3], row[1::3], row[2::3], strict=True):
            dx = signed(dx)
            attr = (flags_tile & 0x80) >> 1
            if face:
                dx = -dx - 9
                attr ^= 0x40
            if 0 <= x + dx <= 255:
                oam.append((next(slots), (y + dy) & 255, flags_tile & 0x7e, attr, x + dx))
    return oam


def color_pixels(oam, chr_data, palette):
    """Rasterize with lower OAM indices in front, recording NES color IDs."""
    pixels = {}
    for _, y, tile, attr, x in sorted(oam):
        assert tile % 2 == 0 and attr & ~0x43 == 0
        for row in range(min(16, 239 - y)):
            line = tile * 16 + 16 * (row // 8) + row % 8
            for column in range(min(8, 256 - x)):
                bit = column if attr & 0x40 else 7 - column
                color = ((chr_data[line] >> bit) & 1) | (((chr_data[line + 8] >> bit) & 1) << 1)
                if color:
                    pixels.setdefault((x + column, y + 1 + row), palette[(attr & 3) * 4 + color])
    return pixels


def verify(donor, poses, offsets, data, tiles, chr_data, atlas, samples, known_anchors):
    tile_map = {tile: index * 2 for index, tile in enumerate(tiles)}
    palette = bytes.fromhex(samples[0]['sprite_palette'])
    assert palette == bytes.fromhex('0f0020050f2716200f150f300f160230')

    def remap(rows):
        return [(slot, y, tile_map[tile], attr, x) for slot, y, tile, attr, x in rows]

    cpu_cases = 0
    for (actor, pose), face, x in itertools.product(poses, (RIGHT, LEFT), range(256)):
        y = (0, 1, 31, 200, 239, 255)[x % 6]
        start = x % 63 + 1
        layers = [(actor, pose, face, x, y)]
        expected = remap(donor.render(layers, start))
        assert decode(offsets, data, layers, start) == expected, (pose, face, x, y)
        cpu_cases += 1

    native, used_pixels = {}, 0
    body_poses = [pose for actor, pose in poses if actor == 0]
    upper_poses = [pose for actor, pose in poses if actor == 1]
    for sample in samples:
        assert sample['dma_page'] == 2 and sample['dma_prg'] == 115261 and sample['ppu_control'] & 0x20
        assert bytes.fromhex(sample['sprite_palette']) == palette
        observed = [tuple(row) for row in sample['oam'] if row[0] != 0]
        assert len(observed) + 1 == len(sample['oam'])
        anchors = known_anchors.get(sample['name'])
        visible_patterns = {tile: (address, bytes.fromhex(pattern))
                            for tile, address, pattern in sample['visible_patterns']}
        for _, _, tile, _, _ in observed:
            address, pattern = visible_patterns[tile]
            assert address == tile * 16 and chr_data[address:address + 32] == pattern
        seen = Counter(row[1:] for row in observed)
        found = []
        for body, upper, lift in itertools.product(body_poses, upper_poses, (0, 8)):
            layers = [(1, upper, LEFT, ANCHOR_X, ANCHOR_Y + lift), (0, body, LEFT, ANCHOR_X, ANCHOR_Y)]
            nominal = donor.render(layers, 1)
            delta = min(row[1] for row in observed) - min(row[1] for row in nominal)
            if anchors is not None and anchors != (ANCHOR_Y + delta, ANCHOR_Y + delta + lift):
                continue
            layers = [(actor, pose, face, x, y + delta) for actor, pose, face, x, y in layers]
            shifted = Counter(((y + delta) & 255, tile, attr, x) for _, y, tile, attr, x in nominal)
            if shifted != seen:
                continue
            for start in sorted(row[0] for row in observed):
                expected = donor.render(layers, start)
                if sorted(expected) == sorted(observed):
                    found.append((body, upper, lift, ANCHOR_Y + delta, start, layers))
        assert len(found) == 1, (sample['name'], found)
        body, upper, lift, y, start, layers = found[0]
        assert lift == (8 if sample['name'] in ('crouch', 'crouch-sword') else 0)
        packed = decode(offsets, data, layers, start)
        assert sorted(packed) == sorted(remap(observed))
        pixels = color_pixels(observed, chr_data, palette)
        assert pixels == color_pixels(packed, atlas, palette)
        used_pixels += len(pixels)
        native[sample['name']] = dict(frame=sample['frame'], body=body, upper=upper, upper_y_offset=lift,
                                      anchor_y=y, oam_start_slot=start, parts=len(packed), pixels=len(pixels))

    actor_cases, overlap_example = 0, set()
    for body, upper, body_face, upper_face in itertools.product(body_poses, upper_poses, (RIGHT, LEFT), (RIGHT, LEFT)):
        lift = 8 if body == 22 else 0
        layers = [(1, upper, upper_face, ANCHOR_X, ANCHOR_Y + lift), (0, body, body_face, ANCHOR_X, ANCHOR_Y)]
        for start in (1, 3, 31, 33, 63):
            original = donor.render(layers, start)
            packed = decode(offsets, data, layers, start)
            pixels = color_pixels(original, chr_data, palette)
            assert packed == remap(original) and pixels == color_pixels(packed, atlas, palette)
            if (body, upper, body_face, upper_face) == (12, 11, LEFT, LEFT):
                overlap_example.add(tuple(sorted(pixels.items())))
            actor_cases += 1
    assert len(overlap_example) == 2  # Rotated priority affects real pixels during a sword phase.
    return native, palette, dict(single_layer_CPU=cpu_cases, composed_layers=actor_cases,
                                 native_OAM_matches=len(native), native_palette_pixels=used_pixels,
                                 overlap_example_distinct_priority_outcomes=len(overlap_example))


def assembly(offsets, data, portrait, palette):
    def block(name, values):
        return name + ':\n' + ''.join('    .byte ' + ','.join(f'${v:02x}' for v in values[i:i + 16]) + '\n'
                                     for i in range(0, len(values), 16))

    return ('; Generated by build_getsu_fuma_art_1110.py from the pinned donor.\n'
            '; Original basic-sword action-zone poses. $ff marks an undefined pose.\n'
            '; Records are count, then signed dx, signed dy, even tile with attr bit 6 in bit 7.\n'
            '; Face 0 uses stored dx/attr. Face 1 uses -dx-9 and XOR $40 on attr.\n'
            '; Process upper layer first. While crouching, add 8 to its OAM Y anchor.\n'
            '; Palette 0 visible colors only. Do not queue the mirrored backdrop at $3f10.\n'
            '; Portrait is five OAM entries, Y/tile/attr/X, for source left-facing idle.\n'
            '.export GfPoseOffsets, GfPoseRecords, GfPortraitOam, GfSpriteColors\n'
            + block('GfPoseOffsets', offsets) + block('GfPoseRecords', data)
            + block('GfPortraitOam', portrait) + block('GfSpriteColors', palette[1:4]))


def build(output):
    assert digest(ROM) == PIN
    for path, sha in INPUTS.items():
        assert digest(path) == sha, path
    with (CAPTURE / 'writers.csv').open() as stream:
        writers = list(csv.DictReader(stream))
    ingresses = {(row['after_pc'], row['prg_offset'], row['ram']) for row in writers}
    assert {('807c', '1407c', '0011'), ('807f', '1407f', '0010'),
            ('808d', '1408d', '0002'), ('8092', '14092', '0003')} <= ingresses
    # Crouch and head-contact poses can yield identical OAM at different anchors.
    # The native writers disambiguate the two crouch observations.
    known_anchors = {}
    for phase in ('crouch', 'crouch-sword'):
        anchors = []
        for pc, address in (('e24d', '0340'), ('e29e', '0341')):
            values = {(int(row['min']), int(row['max'])) for row in writers
                      if (row['phase'], row['after_pc'], row['ram']) == (phase, pc, address)}
            assert len(values) == 1
            low, high = values.pop()
            assert low == high
            anchors.append(low)
        known_anchors[phase] = tuple(anchors)
    raw = ROM.read_bytes()
    assert raw[:16] == bytes.fromhex('4e45531a081070183000000000000001')
    chr_data = raw[16 + PRG_SIZE:]
    source = source_poses(raw)
    body = sorted(set(source['walk_body']) | {source['idle'], source['crouch'], source['head_contact']})
    upper = sorted(set(source['walk_upper']) | set(source['sword']))
    poses = [(0, pose) for pose in body] + [(1, pose) for pose in upper]
    donor = DonorOam(raw)
    offsets, data, tiles = encode(donor, poses)
    art = b''.join(chr_data[tile * 16:tile * 16 + 32] for tile in tiles)
    assert len(art) == 32 * len(tiles)
    atlas = art.ljust(1024, b'\0')
    capture = json.loads((CAPTURE / 'observations.json').read_text())
    assert capture['controller_only']
    native, palette, tests = verify(donor, poses, offsets, data, tiles, chr_data, atlas,
                                    capture['checkpoints'], known_anchors)

    idle = native['idle']
    portrait_layers = [(1, idle['upper'], LEFT, 132, 190), (0, idle['body'], LEFT, 132, 190)]
    original = donor.render(portrait_layers, 1)
    packed = decode(offsets, data, portrait_layers, 1)
    portrait = bytes(byte for _, *row in packed for byte in row)
    portrait_pixels = color_pixels(original, chr_data, palette)
    assert len(portrait) == 20 and portrait_pixels == color_pixels(packed, atlas, palette)
    contiguous = [(index, *row[1:]) for index, row in enumerate(packed)]
    assert portrait_pixels == color_pixels(contiguous, atlas, palette)
    points = list(portrait_pixels)
    bounds = [min(x for x, _ in points), min(y for _, y in points),
              max(x for x, _ in points), max(y for _, y in points)]

    files = {'atlas.chr': atlas, 'poses.inc': assembly(offsets, data, portrait, palette).encode('ascii')}
    for name, content in files.items():
        (output / name).write_bytes(content)
    result = dict(passed=True, donor_SHA256=PIN, donor_renderer='physical 8 KiB PRG10:$807A',
                  donor_pose_table='$81C2, native $F7 != 1 lane', source=source, tests=tests,
                  native_matches=native, body_poses=body, upper_poses=upper,
                  bytes=dict(chr_content=len(art), chr_page=len(atlas), pose_offsets=len(offsets),
                             pose_records=len(data), portrait=len(portrait), palette=3),
                  tiles=[dict(donor_tile=tile, donor_chr_offset=tile * 16, atlas_tile=index * 2)
                         for index, tile in enumerate(tiles)],
                  portrait=dict(face=LEFT, anchor=[132, 190], oam_hex=portrait.hex(),
                                opaque_pixels=len(points), inclusive_pixel_bounds=bounds),
                  palette=dict(index=0, ppu_start=0x3f11, colors=palette[1:4].hex()),
                  scope=dict(host_slot_granted=False, source_family='basic sword, ordinary action-zone actor',
                             known_remaining=['host CHR/OAM admission', 'equipment, hurt and death art',
                                              'OAM priority at overlapping sword poses']),
                  inputs={str(path): digest(path) for path in (*INPUTS, Path(__file__))},
                  outputs={name: digest(output / name) for name in files})
    (output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(ROOT / 'build')
    output.mkdir(exist_ok=True)
    receipt = build(output)
    print(json.dumps({key: receipt[key] for key in ('passed', 'tests', 'bytes', 'portrait')}))


if __name__ == '__main__':
    main()
