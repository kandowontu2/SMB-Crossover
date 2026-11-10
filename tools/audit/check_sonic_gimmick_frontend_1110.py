"""Memory-only Sonic family menu proposal; native runtime admission is separate."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from copy import deepcopy

import check_remaining_roster_starts_1110 as Menu
import stage_thomas_powerup_1110 as Parent
import audit_bub_menu_frontend_1102_v1 as Calls
from check_tmnt_render_oa import address, location

R = Parent.R
sys.path.insert(0, str(R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

PIN = Parent.PIN
SOURCE = R/'tools/reference/sonic_gimmick_frontend_1110.s'


def offset(bank, pc):
    return 16 + bank*8192 + (pc & 8191)


def proposal(raw):
    assert sha256(raw).hexdigest() == PIN
    code = Asm.assemble(SOURCE.read_text(), {
        'RESOLVE': (0xa091, 69), 'TAIL': (0xade8, 23), 'PENDING': (0xbced, 32),
        'NAME': (0xac7d, 40), 'COLORS': (0xbaa4, 85)})
    assert code['symbols']['SonicFamilyCold'] == 0xade8
    assert code['symbols']['SonicFamilyID'] == 0xadf6
    assert code['symbols']['SonicFamilyResolve'] == 0xa0a0
    assert code['used'] == dict(RESOLVE=69, TAIL=23, PENDING=32, NAME=32, COLORS=85), code['used']
    # Current Mini resolver, then the source-owned old Mario table/cold tail.
    # Retire the sole same-bank AltTail stub caller and the dead table10 byte.
    assert raw[offset(124, 0xade8):offset(124, 0xadff)] == bytes.fromhex('00eaeaeaeaea4c25a0a9008dfe5f8de55f8de85f4cd0a9')
    assert raw[offset(124, 0xa0a1):offset(124, 0xa0a4)] == bytes.fromhex('bd40a0')
    assert raw[offset(124, 0xa091):offset(124, 0xa0a1)] == bytes.fromhex('08984a4a4a1869014a18692028090060')
    assert raw[offset(124, 0xac35):offset(124, 0xac38)] == bytes.fromhex('4ceead')
    bank = raw[offset(124, 0xa000):offset(124, 0xa000)+8192]
    assert [i for i in range(len(bank)-2) if bank[i] in (0x20,0x4c)
            and bank[i+1:i+3] == bytes.fromhex('eead')] == [0xc35]
    assert bytes.fromhex('a9ee8d6c01a9ad8d6d01a9fc') not in raw
    # The named grants remain the source of ownership, not padding scans.
    original = (R/'tools/audit/prepare_mr_gimmick_family_1102_v18.py').read_text()
    assert "navbin,'Same214B navigation lease" in original
    assert "body+bytes([0xea])*4,'Same32B static pending shim" in original
    sonic = (R/'tools/audit/check_sonic_sms_native_prototype_1110.py').read_text()
    assert "('NAME_GATE',0xac7d,40)" in sonic and "('COLORS',0xbaa4,85)" in sonic
    assert 'Mike_reserved_cycle_tail=[0xade9,0xadee]' in sonic
    image = bytearray(raw)
    patches = []

    def put(at, data, role):
        old = raw[at:at+len(data)]
        assert len(old) == len(data)
        assert all(at >= p['offset']+len(bytes.fromhex(p['new'])) or at+len(data) <= p['offset'] for p in patches)
        patches.append(dict(offset=at, old=old.hex(), new=data.hex(), role=role))
        image[at:at+len(data)] = data

    for name, bank, pc, size in (('RESOLVE',124,0xa091,69), ('TAIL',124,0xade8,23), ('PENDING',76,0xbced,32),
                                ('NAME',66,0xac7d,40), ('COLORS',62,0xbaa4,85)):
        put(offset(bank, pc), code['images'][name].ljust(size, b'\xea'), name)
    packet = bytes.fromhex('a9f18d6c01a9ad8d6d01a9fc')
    assert raw.count(packet) == 1
    at = raw.index(packet)
    put(at+1, b'\xe8', 'Same native cold operations, relocated in retired source tail')
    put(offset(124,0xac35), bytes.fromhex('4c25a0'), 'Retire sole AltTail stub, retain exact focused DK resolver')
    focused = raw[offset(124,0xa025):offset(124,0xa040)]
    assert focused.count(bytes.fromhex('4ca1a0')) == 1
    put(offset(124,0xa025)+focused.index(bytes.fromhex('4ca1a0'))+1,
        b'\xa0', 'Same focused resolver, shifted by one-byte cursor-high factor')
    toggle = raw[offset(66,0xb02e):offset(66,0xb07c)]
    pattern = bytes.fromhex('eefe5faefe5fe003')
    assert toggle.count(pattern) == 1
    put(offset(66,0xb02e)+toggle.index(pattern)+7, b'\x04', 'Four-state family cycle')
    for pc, old, new in ((0xadd2,11,10), (0xade7,10,0)):
        assert raw[offset(124,pc)] == old
        put(offset(124,pc), bytes((new,)), 'Retire old Mario10 proxy from legal cycle')
    return bytes(image), dict(parent_SHA256=PIN, ROM_SHA256=sha256(image).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(), patches=patches,
        source_grants=dict(navigation=214, pending=32, name=40, colors=85),
        new_RAM_bytes=0, new_PRG_bytes=0, runtime_admission_pending=True)


def main():
    raw, _ = Parent.reconstruct()
    image, record = proposal(raw)
    q = Menu.inventory(image)
    family = [r for r in q['rows'] if r['slot'] == 25]
    mario = [r for r in q['rows'] if r['slot'] == 0]
    assert [r['name'] for r in family] == ['MR GIMMICK','BUB','BOB','SONIC'], family
    assert [r['raw'] for r in family] == [26,39,39,43], family
    assert len(mario) == 10 and 'SONIC' not in [r['name'] for r in mario], mario
    assert q['distinct_named_entries'] == 100 and not q['locked'], q['locked']
    parity = regressions(raw, image)
    print(json.dumps(dict(passed=True, source_CPU_only=True, Mesen_run=False,
        ROM_written=False, output_files=0, family=family, Mario_entries=len(mario),
        distinct_names=100, record=record, parity=parity,
        native_runtime_pending=True), sort_keys=True), flush=True)


def application(m):
    return (bytes(m[:0x100]), bytes(m[0x200:0x800]), bytes(m[0x5fe0:0x8000]),
            tuple(bytes(x) for x in m.ram), bytes(m.vram), tuple(m.chr_latches), m.upper)


def regressions(raw, image):
    bundles = [Menu.W.bundle(data) for data in (raw, image)]
    original_inventory = Menu.inventory(raw)
    # The existing public helper still has its original address. Only its
    # internal CLC/ADC changes to ORA; complete byte-Y range is exercised.
    for i,b in enumerate(bundles):
        row = deepcopy(b['syms']['NrMenuCharacter'])
        row['val'] = hex(0xa091)
        b['syms']['SonicCursorHiTest'] = row
        assert ((location(b, 'SonicCursorHiTest')-16)//8192)|128 == 252
        row = deepcopy(row)
        row['val'] = hex((0xadf1,0xade8)[i])
        b['syms']['SonicColdTest'] = row
    seeds = [Menu.I.UI.seed(b, 0) for b in bundles]
    hi = 0
    for y in range(256):
        for flags in (0x30,0x31,0x74,0xf1):
            results = []
            for seed in seeds:
                m = Menu.I.N.fork(seed)
                z = Calls.invoke(m, 'SonicCursorHiTest', a=85, x=91, y=y, p=flags)
                results.append((m,z))
            assert all(results[0][1][n] == results[1][1][n] for n in ('A','X','Y','P'))
            assert application(results[0][0]) == application(results[1][0]), ('cursor-high',y,flags)
            hi += 1
    cold = 0
    for family in range(4):
        for alts,groups in ((0,0),(255,128),(128,255),(85,170)):
            outputs = []
            for seed in seeds:
                m = Menu.I.N.fork(seed)
                m[0x5ffe],m[0x5fe5],m[0x5fe8] = family,alts,groups
                z = Calls.invoke(m,'SonicColdTest',a=85,x=7,y=91,p=0x71)
                outputs.append((m,z))
                assert (m[0x5ffe],m[0x5fe5],m[0x5fe8]) == (0,0,0)
            assert application(outputs[0][0]) == application(outputs[1][0]), ('cold',family,alts,groups)
            assert all(outputs[0][1][n] == outputs[1][1][n] for n in ('A','X','Y','P'))
            cold += 1
    foreign = 0
    names_checked = set()
    for slot in range(32):
        pair = [Menu.I.UI.seed(b, slot) for b in bundles]
        length = 10 if slot == 0 else 3 if slot == 25 else len([r for r in original_inventory['rows'] if r['slot']==slot])
        for cycle in range(length):
            names = [Menu.menu_name(m)[0] for m in pair]
            assert names[0] == names[1], (slot,cycle,names)
            names_checked.add((slot,Menu.I.N.get(pair[0],'SelectedCharacter'),names[0]))
            assert application(pair[0]) == application(pair[1]), ('foreign-menu',slot,cycle,names)
            for key in (16,128,1,2,4,8):
                models = [Menu.I.N.fork(m) for m in pair]
                results = [Menu.I.UI.key(m,key) for m in models]
                assert application(models[0]) == application(models[1]), ('foreign-input',slot,cycle,names,key)
                assert all(results[0][n] == results[1][n] for n in ('A','X','Y','P'))
            for m in pair:
                Menu.I.UI.key(m,32)
            foreign += 1
    # The Simon family has two distinct selector states for the same name.
    assert len(names_checked) == 99 and foreign == 100, (len(names_checked),foreign)
    return dict(cursor_high_full_Y_flag_cases=hi, cold_actual_full_initializer=cold,
                old_named_profiles=len(names_checked), old_selector_states=foreign,
                old_profile_start_A_and_directions=foreign*6,
                application_PPU_CHR_registers_exact=True)


if __name__ == '__main__':
    main()
