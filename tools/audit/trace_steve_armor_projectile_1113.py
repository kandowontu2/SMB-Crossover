"""Read the original cartridge's armored punch object through real frames."""

import json

import trace_steve_shatterhand_donor_1111 as Donor
import trace_steve_shatterhand_upgrades_1111 as Upgrade
import steve_armor_art_1112 as Art


def trace():
    seed = Upgrade.initialized_companion(Donor.boot(Donor.DONOR.read_bytes()))
    seed.memory[0x05c4] = 0x15
    for age in range(1, 251):
        Donor.frame(seed, 0)
        if seed.memory[0x05c2]:
            break
    assert age == 159
    episodes = []
    art = {}
    host = Art.D.HOST.read_bytes()
    atlases = Art.atlas(Donor.DONOR.read_bytes())[0]
    for face, turn in ((0, []), (128, [64]*16+[0]*4)):
        cpu = Donor.fork(seed)
        for pad in turn:
            Donor.frame(cpu, pad)
        rows, moves, deaths = [], [], []
        pending = None

        def point():
            m = cpu.memory
            return dict(actor=m[0x60f], xq4=m[0xaf]+256*m[0xbf],
                        yq4=m[0xcf]+256*m[0xdf], life=m[0x61f],
                        shape=m[0x65f], pose_low=m[0x66f], age=m[0x6ef],
                        animation_delay=m[0x6cf], animation_step=m[0x6df], facing=m[0x68f])

        def observe(current):
            nonlocal pending
            key = current.memory.code_key(current.pc)
            if key == (13, 0xa86e) and current.x == 15:
                pending = point()
            elif key == (13, 0xa88a) and current.x == 15:
                assert pending is not None
                after = point()
                assert (after['xq4']-pending['xq4']) & 65535 == (0xffc0 if pending['facing']&128 else 0x40)
                moves.append((epoch, pending['xq4'], after['xq4'], pending['life']))
                pending = None
            elif key == (13, 0xa8c1) and current.x == 15:
                deaths.append((epoch, point()))

        previous = None
        for epoch in range(96):
            Donor.frame(cpu, 2 if epoch == 0 else 0, observe)
            sample = point()
            if sample['actor']:
                m = cpu.memory
                pose = m[0x66f]+256*m[0x67f]
                if pose not in art:
                    declared, parts = Art.Art.Geometry.parts(Donor.DONOR.read_bytes(), pose)
                    cells = []
                    r0,r1,r2,r3,r4,r5 = m.registers[:6]
                    large = (r0&254,r0|1,r1&254,r1|1)
                    windows = (r2,r3,r4,r5)+large if m.bank_select&128 else large+(r2,r3,r4,r5)
                    for dy,dx,tile,attr in parts:
                        address = (tile&1)*4096+(tile&254)*16
                        page = windows[address//1024]
                        offset = address&1023
                        cell = bytes(m.ppu_read(address+i) for i in range(32))
                        hits = [(p,index*2) for p,row in ({p:Art.page(host,p) for p in (339,710,711)}|atlases).items()
                                for index in range(32) if row[index*32:index*32+32] == cell]
                        cells.append(dict(y=dy,x=dx,tile=tile,attr=attr,source_page=page,
                                          source_offset=offset,existing_art_matches=hits))
                    art[pose] = dict(declared_page=declared,registers=list(m.registers[:6]),cells=cells)
            if sample['actor'] or sample['actor'] != previous:
                rows.append(dict(update=epoch, **sample))
            previous = sample['actor']
        assert moves
        episodes.append(dict(requested_face=face, actual_facing=cpu.memory[0x5b2],
                             frames=rows, motion_steps=moves, source_death_entries=deaths))
    return dict(donor=Donor.PIN, matching_robot_and_pattern_fixture=True,
                armor_entered_after=159, episodes=episodes, actual_pattern_art=art, output_files=0)


if __name__ == '__main__':
    print(json.dumps(trace(), sort_keys=True), flush=True)
