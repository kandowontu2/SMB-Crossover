"""Qualify Getsu's resident pose codec against donor OAM and the native renderer."""

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re

from py65.devices.mpu6502 import MPU

import build_getsu_fuma_art_1110 as Donor
import check_getsu_fuma_owner_1110 as Owner
from check_mega_giant_compound_1110 import vector
from check_mega_giant_ppu_mapping_1110_v1 import sprite_pair
from check_tmnt_render_oa import address, location


R, N = Owner.R, Owner.N
START, LIMIT = 0xa4be, 0xa800
SOURCE = R / 'tools/reference/getsu_fuma_host_render_1110.s'
ART = Owner.Page.ASSET.parent
PREVIOUS = R / 'build/getsu-fuma-owner-1110/kernel.bin'
STATE = {f'Gf{name}': Owner.STATE + i for i, name in enumerate(Owner.Host.FIELDS)}


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def assemble(output, b):
    src = SOURCE.read_text()
    imports = {name for row in src.splitlines() if row.startswith('.import ')
               for name in row.removeprefix('.import ').split(', ')}
    symbols = STATE | {name: address(b, name) for name in imports - STATE.keys()}
    for name, bank in (('MetaspriteRenderLoop', 4), ('X5SetPhysicalChr', 62)):
        assert (location(b, name) - 16) // 8192 == bank and 0xa000 <= symbols[name] < 0xc000
    defines = ''.join(f'{name}=${symbols[name]:04x}\n' for name in sorted(imports))
    src = defines + re.sub(r'^\.import .+\n', '', src, flags=re.M)
    art = (ART / 'poses.inc').read_text().replace(', GfPortraitOam', '')
    art = re.sub(r'GfPortraitOam:\n.*?(?=GfSpriteColors:)', '', art, flags=re.S)
    src += '\n' + art
    code, labels = Owner.assemble(output, src, (('DRAW', START, LIMIT - START, ('GETSU_HOST_RENDER',)),))
    assert labels['GfDraw'] == START and labels['GfPoseOffsets'] == labels['GfDrawEnd']
    return code, labels


def loaded(output, b, code):
    meta = json.loads(PREVIOUS.with_name('proof.json').read_text())
    assert meta['passed'] and meta['parent_SHA256'] == Owner.PIN and sha(PREVIOUS) == meta['kernel_SHA256']
    prior = PREVIOUS.read_bytes()
    end = START - Owner.CODE
    assert meta['kernel_bytes'] == end and prior[end:] == b'\xff' * (len(prior) - end)
    atlas = (ART / 'atlas.chr').read_bytes()
    Owner.physical(b, atlas)
    old_worker, new_worker = Owner.worker(output, b)
    typed, _ = Owner.assemble(output, Owner.TYPED.read_text(), (('REMOTE', 0xb1ba, 81, ('TYPED',)),))
    trial, _, cookie, body = Owner.image(b, prior[:end] + code, typed, old_worker, new_worker, atlas)
    offset = Owner.Page.CHR + 990 * 1024
    raw = trial['raw']
    trial['raw'] = raw[:offset] + atlas + raw[offset + 1024:]
    machine = Owner.blank(trial)
    result = Owner.cold(machine, 42)
    assert Owner.headers(machine) == (cookie, cookie) and bytes(machine.ram[3][:2048]) == body
    assert result['PPU_reads'] == 4100
    N.put(machine, DisableScreenFlag=0, NmiDisable=255)
    machine[0x5101] = 3  # The host's 1 KB CHR mode during active MMC5 play.
    Owner.clear_logs(machine)
    return machine, cookie, body, result


def direct(cpu, pc):
    cpu.pc, cpu.sp, cpu.p = pc, 0xfd, 0x30
    cpu.stPushWord(0x5aff)
    for _ in range(300):
        if cpu.pc == 0x5b00:
            assert cpu.sp == 0xfd
            return
        assert cpu.memory[cpu.pc] != 0, hex(cpu.pc)
        cpu.step()
    raise AssertionError(('Donor walk return bound', hex(pc), hex(cpu.pc)))


def gait(raw, code, labels):
    donor, host = MPU(), MPU()
    donor.memory[0xc000:] = Donor.fixed(raw, 0xc000, 0x4000)
    host.memory[START:START + len(code)] = code
    cases = 0
    for action, speed, timer, index, face in product((0, 1, 2, 4), (-384, -65, -1, 0, 1, 65, 384),
                                                     (0, 1, 255, 256, 2048), (0, 1, 3, 4), (0, 1)):
        src = {0x4f: action, 0x3f0: speed & 255, 0x3f8: (speed >> 8) & 255, 0x3f1: timer & 255,
               0x3f9: timer >> 8, 0x3d: index, 0x1c4: face, 0x300: 12, 0x3c0: 0, 0x301: 3, 0x3c1: 0}
        dst = (STATE['GfAction'], STATE['GfVXLo'], STATE['GfVXHi'], 0xc024, 0xc025, 0xc023,
               STATE['GfFacing'], STATE['GfBodyPose'], STATE['GfBodyFacing'], 0xc028, 0xc029)
        for (key, value), target in zip(src.items(), dst, strict=True):
            donor.memory[key] = host.memory[target] = value
        donor.memory[0x50] = 1
        direct(donor, 0xee67)
        direct(host, labels['GfWalkAdvance'])
        assert [donor.memory[k] for k in src] == [host.memory[k] for k in dst], (action, speed, timer, index, face)
        cases += 1
    return cases


def parts(donor, tile_map, body, upper, body_face, upper_face, crouch, x, y):
    rows = donor.render([(1, upper, upper_face, 128, 160 + 8 * crouch),
                         (0, body, body_face, 128, 160)], 1)
    return [(oy + y - 160, tile_map[tile], attr, ox + x - 128) for _, oy, tile, attr, ox in rows]


def render(seed, labels, donor, tile_map):
    poses = [(12, 3, 0), (4, 1, 0), (5, 2, 0), (6, 3, 0), (22, 1, 1),
             (37, 2, 0), (12, 7, 0), (12, 8, 0), (12, 9, 0), (22, 10, 1), (22, 11, 1)]
    tested = accepted = capacity = first_ppu = 0
    max_cycles = 0
    for (body, upper, crouch), body_face, upper_face, (px, py), (cursor, rotation) in product(
            poses, (0, 1), (0, 1), ((-9, 176), (42, 176), (247, 176), (126, -35), (126, 231)),
            ((0, 0), (16, 0), (16, 224), (224, 8), (228, 60), (252, 0))):
        m = N.fork(seed)
        ax, ay = px + 8, py + 32
        world_x = 256 + px
        oy = py + 256
        N.put(m, Player_X_Position=world_x & 255, Player_PageLoc=world_x >> 8,
              ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=1, Player_Y_Position=oy & 255, Player_Y_HighPos=oy >> 8,
              CurrentOAMOffset=cursor, GuestOamRotationActive=int(bool(rotation)), RgOamRotation=rotation,
              VRAM_Buffer1_Offset=0, StarInvincibleTimer=0, GuestPowerupActive=0)
        m[STATE['GfAction']], m[STATE['GfBodyPose']], m[STATE['GfBodyFacing']] = crouch, body, body_face
        m[0xc020], m[0xc028], m[0xc029] = 1, upper, upper_face
        m[0x200:0x300] = bytes([0xf8]) * 256
        rows = parts(donor, tile_map, body, upper, body_face, upper_face, crouch, ax, ay)
        result = Owner.invoke(m, labels['GfDraw'], bank=3)
        max_cycles = max(max_cycles, result['CPU'])
        tested += 1
        assert m.rawtags == seed.rawtags
        assert m[0xc040] == 4 * len(rows), (body, upper, m[0xc040], len(rows))
        if cursor + 4 * len(rows) >= 256:
            assert not result['P'] & 1 and bytes(m[0x200:0x300]) == bytes([0xf8]) * 256
            assert N.get(m, 'VRAM_Buffer1_Offset') == 0
            capacity += 1
            continue
        assert result['P'] & 1 and N.get(m, 'CurrentOAMOffset') == cursor + 4 * len(rows)
        assert N.get(m, 'CurrentCHRBank') == 222 and N.get(m, 'X5ChrMode') == 0x83
        assert N.get(m, 'VRAM_Buffer1_Offset') == 6
        buf = address(m.bundle, 'VRAM_Buffer1')
        assert bytes(m[buf:buf + 7]) == bytes.fromhex('3f110300200500')
        for i, (y, tile, attr, x) in enumerate(rows):
            offset = (cursor + rotation + 4 * i) & 255
            at = 0x200 + offset
            if 0 <= x <= 255 and 0 <= y <= 255:
                assert bytes(m[at:at + 4]) == bytes((y, tile, attr, x)), (body, upper, i, px, py, bytes(m[at:at + 4]))
            else:
                assert m[at] == 0xf8, (body, upper, i, px, py)
        accepted += 1
        if not first_ppu and (px, py, cursor) == (42, 176, 16):
            Owner.invoke(m, address(m.bundle, 'X5PublishChr'), bank=0xbe)
            atlas = (ART / 'atlas.chr').read_bytes()
            for _, tile, _, _ in rows:
                assert sprite_pair(m, tile) == atlas[tile * 16:tile * 16 + 32]
                first_ppu += 1
    return dict(cases=tested, accepted=accepted, capacity_rejects=capacity, mapped_patterns=first_ppu, max_CPU=max_cycles)


def palette_lifecycle(seed, labels):
    m = N.fork(seed)
    base = address(m.bundle, 'VRAM_Buffer1')
    draw = labels['GfDraw']
    N.put(m, Player_X_Position=48, Player_Y_Position=176, Player_Y_HighPos=1, VRAM_Buffer1_Offset=78)
    m[base + 78:base + 85] = bytes([0xb9]) * 7
    assert Owner.invoke(m, draw, bank=3)['P'] & 1
    assert m[0xc030] == 0 and bytes(m[base + 78:base + 85]) == bytes([0xb9]) * 7
    N.put(m, CurrentOAMOffset=16, VRAM_Buffer1_Offset=0, ReloadCHRBank=0, StarInvincibleTimer=5)
    assert Owner.invoke(m, draw, bank=3)['P'] & 1
    assert N.get(m, 'VRAM_Buffer1_Offset') == N.get(m, 'ReloadCHRBank') == m[0xc030] == 0
    N.put(m, CurrentOAMOffset=16, StarInvincibleTimer=0)
    assert Owner.invoke(m, draw, bank=3)['P'] & 1
    assert bytes(m[base:base + 7]) == bytes.fromhex('3f110300200500')
    assert N.get(m, 'VRAM_Buffer1_Offset') == 6 and m[0xc030] == 1
    N.put(m, CurrentOAMOffset=16, VRAM_Buffer1_Offset=0, GuestPowerupActive=1)
    assert Owner.invoke(m, draw, bank=3)['P'] & 1 and m[0xc030] == 0
    assert N.get(m, 'VRAM_Buffer1_Offset') == 0
    N.put(m, CurrentOAMOffset=16, GuestPowerupActive=0)
    assert Owner.invoke(m, draw, bank=3)['P'] & 1 and m[0xc030] == 1
    N.put(m, CurrentOAMOffset=16, VRAM_Buffer1_Offset=0)
    warm = Owner.invoke(m, draw, bank=3)
    assert warm['P'] & 1 and N.get(m, 'VRAM_Buffer1_Offset') == 0
    return dict(queue_full_retry=True, star_does_not_override=True, transformation_does_not_override=True,
                warm_does_not_requeue=True, warm_CPU=warm['CPU'])


def interrupt_controls(seed, labels):
    from verify_native_relocation import NesMPU

    cuts = (labels['GfDraw'], labels['GfBuildRecord'], address(seed.bundle, 'MetaspriteRenderLoop'),
            address(seed.bundle, 'X5SetPhysicalChr'))
    rows = []

    def run(cut=None, kind=None):
        m = N.fork(seed)
        N.put(m, CurrentOAMOffset=16, VRAM_Buffer1_Offset=0)
        dest = labels['GfDraw']
        m[0x16a], m[0x16c], m[0x16d] = 0, dest & 255, dest >> 8
        cpu = NesMPU(memory=m, pc=0x15a)
        cpu.a, cpu.p, cpu.sp = 3, 0x31, 224
        cpu.stPushWord(0x5aff)
        seen = None
        for _ in range(6000):
            if cpu.pc == 0x5b00:
                break
            if cut == cpu.pc and not seen:
                oam = bytes(m[0x200:0x300])
                state = tuple(bytes(m.ram[k]) for k in (2, 3))
                seen = vector(cpu, kind)
                assert bytes(m[0x200:0x300]) == oam and tuple(bytes(m.ram[k]) for k in (2, 3)) == state
            assert m[cpu.pc], (hex(cpu.pc), m.rawtags)
            cpu.step()
        assert cpu.pc == 0x5b00 and cpu.sp == 224 and bool(seen) == (cut is not None)
        fields = ('CurrentOAMOffset', 'CurrentCHRBank', 'X5ChrMode', 'VRAM_Buffer1_Offset')
        result = (cpu.a, cpu.x, cpu.y, cpu.p & 0xef, tuple(m.rawtags), bytes(m[0x200:0x300]),
                  tuple(bytes(m.ram[k]) for k in (2, 3)), tuple(N.get(m, name) for name in fields))
        return result, seen

    base, _ = run()
    for cut, kind in product(cuts, ('irq', 'nmi')):
        result, witness = run(cut, kind)
        assert result == base
        rows.append(witness)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    b = Owner.Page.bundle()
    assert Donor.digest(Donor.ROM) == Donor.PIN
    raw = Donor.ROM.read_bytes()
    code, labels = assemble(out, b)
    seed, cookie, body, load = loaded(out, b, code)
    art = json.loads(Owner.Page.ASSET.read_text())
    tiles = {row['donor_tile']: row['atlas_tile'] for row in art['tiles']}
    source_gait = gait(raw, code, labels)
    oam = render(seed, labels, Donor.DonorOam(raw), tiles)
    palette = palette_lifecycle(seed, labels)
    interrupts = interrupt_controls(seed, labels)
    report = dict(passed=True, CPU_only=True, ROM_written=False, public_ingress=False,
                  parent_SHA256=Owner.PIN, installed_kernel_bytes=START - Owner.CODE + len(code),
                  draw_address=labels['GfDraw'], free_bytes=LIMIT - START - len(code),
                  full_kernel_SHA256=sha256(body).hexdigest(), cookie=cookie.hex(), labels=labels,
                  cold=load, source_gait=source_gait, native_OAM=oam, palette=palette, interrupts=interrupts,
                  bindings={p.relative_to(R).as_posix(): sha(p) for p in
                            (Path(__file__), SOURCE, PREVIOUS, Owner.Page.ASSET, ART / 'poses.inc', ART / 'atlas.chr')})
    (out / 'proof.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (out / 'render.bin').write_bytes(code)
    print(json.dumps({k: report[k] for k in ('installed_kernel_bytes', 'free_bytes', 'source_gait', 'native_OAM')}))


if __name__ == '__main__':
    main()
