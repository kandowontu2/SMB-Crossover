"""Compare robot damage and destruction to the pinned Shatterhand cartridge."""

from hashlib import sha256
from itertools import product
import json
import argparse

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_throw_1111 as Throw
import check_steve_shatterhand_lift_art_1111 as Art

D, H = Throw.D, Throw.Orbit.H
SOURCE = D.ROOT / 'tools/reference/steve_shatterhand_robot_death_1112.s'
ORIGIN, STOP = 0xab80, 0x5000
ORIGINAL = Throw.ORIGINAL | {'SteveBotHP': (0x06fc,), 'SteveDeathPolarity': (0x05cb,)}
DEATH_ROWS = bytes.fromhex('03dc0103de0103e00103e201ffe201')
ALIASES = {0x55: 0x77, 0x57: 0x79}


def source(fields):
    text = SOURCE.read_text()
    groups = (('Throw', ('SteveThrowTimer', 'SteveThrowSpeed', 'SteveThrowAux', 'SteveThrowAim', 'SteveThrowAnimAux')),
              ('Pose', ('SteveLiftBotAnim', 'SteveLiftBotDelay', 'SteveLiftBotStep', 'SteveBotPose', 'SteveBotPose+1')))
    head, marker, reset = text.partition('SteveRobotDeathReset:\n')
    assert marker
    for label, names in groups:
        addresses = [fields[name] if '+' not in name else fields[name[:-2]]+1 for name in names]
        if addresses != list(range(addresses[0], addresses[0]+5)):
            continue
        # Order of zeroing is unobservable; only these five bytes are owned.
        for name in names:
            line = f'    sta {name}\n'
            assert reset.count(line) == 1
            reset = reset.replace(line, '')
        loop = f'    ldx #4\nRobotClear{label}:\n    sta {names[0]},x\n    dex\n    bpl RobotClear{label}\n'
        reset = reset.replace('    lda #0\n', '    lda #0\n'+loop, 1)
    return head+marker+reset


def link(raw, fields=None, *, origin=ORIGIN):
    assert sha256(raw).hexdigest() == D.PIN
    if fields is None:
        fields = Throw.link(raw)[1] | dict(SteveDeathDraw=0x6200, SteveDeathPolarity=0x6201,
                                           SteveBotHP=0x6202, SteveDeathClearShots=0x6400)
    definitions = ''.join(f'{name} = ${at:04x}\n' for name, at in fields.items())
    linked = H.assemble(definitions + source(fields), {'ROBOT_DEATH': (origin, 512)})
    rows_at = 16+13*8192+(0xbe08 & 8191)
    assert raw[rows_at:rows_at+15] == DEATH_ROWS
    return linked, fields


def invoke(cpu, entry, *, a=0, x=12, y=12, stop=None):
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.pc = a, x, y, 0x21, 0xf0, entry
    cpu.stPushWord(STOP-1)
    for _ in range(1200):
        if stop and cpu.pc in stop:
            return cpu.pc
        if (cpu.pc, cpu.sp) == (STOP, 0xf0):
            return
        assert cpu.memory[cpu.pc], (hex(entry), hex(cpu.pc))
        cpu.step()
    raise AssertionError((hex(entry), hex(cpu.pc)))


class Pair:
    def __init__(self, raw, linked, fields):
        self.donor, self.host = MPU(), MPU()
        self.donor.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
        code = linked['images']['ROBOT_DEATH']
        self.host.memory[ORIGIN:ORIGIN+len(code)] = code
        # This callback models the host's separate projectile type arrays.
        self.host.memory[fields['SteveDeathClearShots']:fields['SteveDeathClearShots']+11] = (
            bytes.fromhex('a20fa9009d0063ca10fa60'))
        self.fields, self.symbols = fields, linked['symbols']

    def seed(self, values):
        d, m = self.donor.memory, self.host.memory
        for name in ORIGINAL:
            value = values.get(name, 0)
            addresses = ORIGINAL[name]
            for address, byte in zip(addresses, value.to_bytes(len(addresses), 'little'), strict=True):
                d[address] = byte
            at = self.fields[name]
            m[at:at+len(addresses)] = value.to_bytes(len(addresses), 'little')
        m[self.fields['SteveDeathDraw']] = 0x9a
        shots = [(i*13+1) & 255 for i in range(16)]
        d[0x700:0x710], m[0x6300:0x6310] = shots, shots

    def compare(self, context):
        for name, addresses in ORIGINAL.items():
            expected = bytes(self.donor.memory[at] for at in addresses)
            at = self.fields[name]
            actual = bytes(self.host.memory[at:at+len(addresses)])
            assert actual == expected, (context, name, actual.hex(), expected.hex())
        assert self.donor.memory[0x700:0x710] == self.host.memory[0x6300:0x6310], context

    def tick(self, context):
        draw = invoke(self.donor, 0xa4c9, stop=(0xa52e, 0xa531)) == 0xa52e
        invoke(self.host, self.symbols['SteveRobotDeathTick'])
        self.compare(context)
        assert self.host.memory[self.fields['SteveDeathDraw']] == draw, context
        return draw


def damage(raw, linked, fields):
    p = Pair(raw, linked, fields)
    p.donor.memory[0x8000:0xa000] = raw[16+8*8192:16+9*8192]
    count, lethal = 0, 0
    for flags, hp, cue in product(range(256), (0, 1, 2, 7, 8, 16, 255), (0, 9)):
        p.seed(dict(SteveBotActor=3, SteveBotAge=0x91, SteveBotAngle=0x39,
                    SteveBotHP=hp, SteveThrowSound=cue, SteveThrowTimer=6,
                    SteveThrowSelector=0x82, SteveBotPose=0x15e))
        p.donor.memory[0x60] = flags
        invoke(p.donor, 0x844e)
        invoke(p.host, p.symbols['SteveRobotDamage'], a=flags)
        p.compare(('damage', flags, hp, cue))
        assert p.host.a == p.donor.a, (flags, hp, cue, p.host.a, p.donor.a)
        lethal += p.host.memory[fields['SteveBotActor']] == 0xff
        count += 1
    return dict(comparisons=count, fatal=lethal)


def contacts(raw):
    """Record actual overlap routing before the accepted damage leaf."""
    cpu = MPU()
    cpu.memory[0x8000:0xc000] = raw[16+8*8192:16+10*8192]
    results = []
    cases = [(flags, age, hp, 60, 0) for flags, age, hp in
             product((1, 0x21), (7, 60), (1, 16))]
    cases += [(1, 60, 16, 11, 0), (1, 60, 16, 60, 1), (0x81, 60, 16, 60, 0)]
    for flags, enemy_age, hp, bot_age, armor in cases:
        m = cpu.memory
        m[0:0x800] = [0]*0x800
        m[0x60] = flags
        # One 16x16 enemy box and the robot centered inside its expansion.
        m[0x61:0x69] = bytes.fromhex('0020002000010001')
        m[0xac], m[0xbc], m[0xcc], m[0xdc] = 0, 0x20, 0, 0x20
        m[0x600], m[0x6e0], m[0x6f0] = 1, enemy_age, 6
        m[0x60c], m[0x6ec], m[0x6fc], m[0x5c2] = 1, bot_age, hp, armor
        m[0x65c], m[0x66c], m[0x67c] = 0x80, 0x5e, 1
        invoke(cpu, 0x83e2, x=0)
        admitted = bot_age >= 12 and armor == 0 and flags < 128
        if admitted:
            cue = 0x35 if flags == 1 and enemy_age >= 8 else 0x33
            assert m[0x6ec] == 0 and m[0xf1] == cue, (
                flags, enemy_age, hp, m[0x6ec], hex(m[0xf1]))
            assert m[0x6fc] == (hp-1 if hp > 1 else hp)
            assert m[0x60c] == (0xff if hp == 1 else 0xc1 if flags == 1 else 1), (
                flags, enemy_age, hp, hex(m[0x60c]), m[0x6fc], m[0x6f0])
            assert m[0x62c] == (32 if hp == 1 else 0)
            assert m[0x6f0] == (4 if flags == 1 and enemy_age >= 8 else 6)
        else:
            assert (m[0x60c], m[0x6ec], m[0x6fc], m[0x6f0], m[0xf1]) == (1, bot_age, hp, 6, 0)
        results.append(dict(flag=flags, enemy_age=enemy_age, bot_hp=hp, bot_age=bot_age, armor=armor,
                            actor=m[0x60c], final_hp=m[0x6fc], enemy_hp=m[0x6f0], timer=m[0x62c],
                            sound=m[0xf1]))
    return results


def destruction(raw, linked, fields):
    p = Pair(raw, linked, fields)
    ticks = 0
    for timer, polarity, phase, y, anim in product((0, 1, 2, 31, 32), (0, 128), range(4),
                                                  (0, 15, 255, 256, 0xfff0, 0xffff), (0x14, 0x20)):
        p.seed(dict(SteveBotActor=255, SteveBotX=0x704f, SteveBotY=y, SteveBotFacing=128,
                    SteveBotAge=0, SteveDeathPolarity=polarity, SteveBotClock=phase,
                    SteveThrowTimer=timer, SteveThrowSelector=0x82, SteveBotHP=1,
                    SteveThrowSpeed=0xa0, SteveThrowAim=0x3c, SteveThrowAux=2,
                    SteveThrowAnimAux=9, SteveLiftBotAnim=anim, SteveBotPose=0x15e,
                    SteveLiftBotDelay=3, SteveLiftBotStep=1))
        p.tick(('step', timer, polarity, phase, y, anim))
        ticks += 1
    traces = []
    for polarity, phase, facing in product((0, 128), range(4), (0, 128)):
        p.seed(dict(SteveBotActor=255, SteveBotX=0x704f, SteveBotY=0x6000,
                    SteveBotFacing=facing, SteveDeathPolarity=polarity, SteveBotClock=phase,
                    SteveThrowTimer=32, SteveThrowSelector=0x80, SteveBotHP=1,
                    SteveLiftBotAnim=0x14, SteveBotPose=0x15e, SteveLiftBotDelay=5,
                    SteveLiftBotStep=1, SteveThrowSpeed=0x60, SteveThrowAux=7,
                    SteveThrowAim=0x1e, SteveThrowAnimAux=4))
        seen, drawn = [], 0
        for tick in range(60):
            p.donor.memory[0x0c] = (phase+tick) & 255
            p.host.memory[fields['SteveBotClock']] = (phase+tick) & 255
            drawn += p.tick(('sequence', polarity, phase, facing, tick))
            pose = p.donor.memory[0x66c]+256*p.donor.memory[0x67c]
            seen.append(pose)
            ticks += 1
            if p.donor.memory[0x60c] == 0:
                break
        assert tick == 44 and drawn == 28 and seen[32:45] == [
            0x1dc, 0x1dc, 0x1dc, 0x1de, 0x1de, 0x1de,
            0x1e0, 0x1e0, 0x1e0, 0x1e2, 0x1e2, 0x1e2, 0]
        assert p.donor.memory[0xf1] == 10
        traces.append(dict(polarity=polarity, phase=phase, facing=facing,
                           ticks=tick+1, drawn=drawn))
    return dict(step_comparisons=ticks, full_sequences=traces)


def graphics(raw, host):
    records, cells = {}, {}
    native = MPU()
    native.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    publications = 0
    for pose, facing, polarity in product((0x1dc, 0x1de, 0x1e0, 0x1e2), (0, 128), (0, 128)):
        native.memory[0x66c], native.memory[0x67c] = pose & 255, pose >> 8
        native.memory[0x68c], native.memory[0x5cb] = facing, polarity
        native.memory[0x6ec], native.memory[0x6fc] = 0, 1
        invoke(native, 0xa6da, stop=(0xc003,))
        assert native.a+256*native.y == pose+bool(facing)
        assert native.memory[0x9e] == polarity | 3
        publications += 1
    for pose in (0x1dc, 0x1de, 0x1e0, 0x1e2):
        page, parts = Art.Geometry.parts(raw, pose, 3)
        assert page == 87 and Art.Geometry.parts(raw, pose+1, 3) == (page, parts)
        records[f'{pose:04x}'] = [(dy, dx, tile, attr & 0xc3) for dy, dx, tile, attr in parts]
        for _, _, tile, _ in parts:
            cell = Art.original_cell(raw, page, tile)
            cells[tile] = dict(donor_page=page, sha256=sha256(cell).hexdigest(), data=cell.hex())
            if tile in ALIASES:
                mapped = ALIASES[tile]
                at = (mapped & 0x3e)*16
                assert Art.T.page(host, 711)[at:at+32] == cell
                cells[tile]['existing_host_tile'] = mapped
    assert len(cells) == 4
    return dict(donor_rows=DEATH_ROWS.hex(), records_with_hurt_palette=records,
                record_bytes=sum(1+len(parts)*4 for parts in records.values()),
                cells={f'{tile:02x}': row for tile, row in cells.items()},
                additional_chr_bytes=64, inverted_attr_xor=128,
                original_pose_publications=publications)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-layout', action='store_true')
    args = parser.parse_args()
    raw, host = D.DONOR.read_bytes(), D.HOST.read_bytes()
    linked, fields = link(raw)
    if args.live_layout:
        import check_steve_throw_controls_live_1111 as Controls
        _, info = Controls.proposal(host, graphics=True)
        fields.update(info['throw_control_fields'])
        fields.update(SteveBotHP=fields['SteveRobotArrival'], SteveDeathDraw=0xc979,
                      SteveDeathPolarity=fields['SteveBotRoomPolarity'])
        linked, fields = link(raw, fields)
    code = linked['images']['ROBOT_DEATH']
    result = dict(donor=sha256(raw).hexdigest(), live_layout=args.live_layout,
                  worker_bytes=len(code), worker_sha256=sha256(code).hexdigest(),
                  entrypoints={name: hex(at) for name, at in linked['symbols'].items()
                               if name in ('SteveRobotDamage', 'SteveRobotDeathTick', 'SteveRobotDeathReset')},
                  damage=damage(raw, linked, fields), original_contacts=contacts(raw),
                  destruction=destruction(raw, linked, fields),
                  graphics=graphics(raw, host), output_files=0, mounted=False)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
