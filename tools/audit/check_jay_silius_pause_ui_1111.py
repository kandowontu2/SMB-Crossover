"""Fund and exercise Jay pause Select on the exact current native UI path."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_jay_silius_shotgun_transport_1111 as T

C, H, J, N, W = T.C, T.H, T.J, T.N, T.W
SOURCE = H.ROOT / 'tools/reference/jay_silius_pause_ui_1111.s'
LAYOUT = {'UI_DISPATCH': (0xa5d8, 60), 'UI_LEGACY': (0xa79c, 24),
          'UI_NATIVE': (0xa6f2, 75), 'PAUSE_SUPPORT': (0xb67b, 133)}
PRIVATE = dict(Ready=0xc033, PreviousSelect=0xc0c8, WeaponReady=0xc0c9, SelectEdge=0xc0ca)


def assemble(aliases, *, update=0xa785):
    constants = dict(aliases, **PRIVATE, JayHot=0xb27f, PrivateUpdate=update, PausedSelect=0xb600)
    text = ''.join(f'{name}=${value:04x}\n' for name, value in constants.items()) + SOURCE.read_text()
    program = H.assemble(text, LAYOUT)
    assert program['used']['UI_DISPATCH'] == 60
    assert program['used']['UI_LEGACY'] == 22
    assert program['used']['UI_NATIVE'] == 74
    assert program['symbols']['GenericCharacter'] == 0xa5e8
    return program


def proposal(raw, *, movement=None):
    image, linked = T.proposal(raw, movement=movement)
    if movement:
        linked = dict(linked, motion=movement)
    return add_pause(raw, image, linked)


def add_pause(raw, image, linked):
    assert T.digest(raw) == T.PIN
    motion = linked.get('motion')
    update = motion['symbols']['PrivateUpdate'] if motion else 0xa785
    program = assemble(linked['aliases'], update=update)
    out = bytearray(image)
    edits = list(linked['edits'])
    for name in ('UI_DISPATCH', 'UI_LEGACY', 'UI_NATIVE'):
        pc, size = LAYOUT[name]
        at = C.offset(86, pc)
        assert raw[at:at+size] == image[at:at+size]
        out[at:at+size] = program['images'][name].ljust(size, b'\xea')
        edits.append((at, size))
    # The one original HudRead call is in the replaced native leaf. All its
    # callers and the external raw41 generic entry remain accounted for.
    bank = raw[C.offset(86, 0xa000):C.offset(86, 0xa000)+8192]
    assert [0xa000+i for i in range(8190) if bank[i:i+3] == b'\x20\xef\xa5'] == [0xa72a]
    assert raw[C.offset(86, 0xa7f8):C.offset(86, 0xa7fb)] == bytes.fromhex('4ce8a5')
    packet = bytearray(T.page(image, T.PACKET_PAGE))
    mux = 64 + 0x303
    assert packet[mux:mux+4] == bytes.fromhex('c0e2f0ba')
    assert packet[mux+11:mux+14] == b'\x4c' + J.u16(update)
    packet[mux:mux+3] = b'\x4c' + J.u16(program['symbols']['PauseMux'])
    carrier = bytearray(linked['carrier'])
    start = LAYOUT['PAUSE_SUPPORT'][0] - 0xb400
    code = program['images']['PAUSE_SUPPORT']
    assert carrier[start:start+len(code)] == b'\xea' * len(code)
    carrier[start:start+len(code)] = code
    rows = (T.page(image, T.MOTION_PAGE) if motion else b'')
    if linked['descriptor'] == T.FULL_DESCRIPTOR:
        assert motion
        rows += T.page(image, T.EXTRA_PAGE)
    stage = T.page(image, 331) + T.page(image, 332)
    cookie = bytes((0xa7, 16, 32, 8)) + sha256(stage + linked['descriptor'] + packet + carrier + rows).digest()[:12]
    cold = T.cold_program(linked['descriptor'], cookie)
    at = C.offset(65, T.COLD)
    out[at:at+T.COLD_SIZE] = cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    hot = C.offset(94, 0xb27f)
    assert out[hot+87:hot+91] == bytes.fromhex('c9e2f0ee')
    out[hot+88], out[hot+89] = 0xe0, 0xd0
    edits.append((hot+88, 2))
    assert out[hot:hot+129].count(linked['cookie']) == 1
    cookie_at = hot + out[hot:hot+129].index(linked['cookie'])
    out[cookie_at:cookie_at+16] = cookie
    for index, data in ((T.PACKET_PAGE, packet), (T.CHR_PAGE, carrier)):
        at = C.CHR + 1024*index
        out[at:at+1024] = data
    linked = dict(linked, cold=cold, cookie=cookie, carrier=bytes(carrier), pause=program,
                  edits=edits, transferred=(bytes(carrier)+rows)[:len(linked['transferred'])])
    return bytes(out), linked


def isolated_parity(raw, program):
    old_mem = [0]*65536
    new_mem = [0]*65536
    at = C.offset(86, 0xa000)
    old_mem[0xa000:0xc000] = raw[at:at+8192]
    new_mem[0xa000:0xc000] = raw[at:at+8192]
    for name in ('UI_DISPATCH', 'UI_LEGACY', 'UI_NATIVE'):
        start, size = LAYOUT[name]
        new_mem[start:start+size] = program['images'][name].ljust(size, b'\xea')
    old, new = MPU(memory=old_mem), MPU(memory=new_mem)
    classifier = 0
    for selected, variant in product(range(256), (0, 32)):
        targets = []
        for cpu, legacy in ((old, 0xa5fe), (new, 0xa79c)):
            cpu.pc, cpu.x = 0xa5d8, selected
            cpu.memory[0x5fe5] = variant
            for _ in range(30):
                if cpu.pc in (0xa5e8, legacy, 0xa7f4):
                    targets.append({0xa5e8: 'generic', legacy: 'legacy', 0xa7f4: 'upper'}[cpu.pc])
                    break
                cpu.step()
            else:
                raise AssertionError(('UI classification', selected, variant, hex(cpu.pc)))
        assert targets[0] == targets[1], (selected, variant, targets)
        classifier += 1
    checks = 0
    for hurt, kind, pad, selected, hud in product((0, 1), range(256), (0, 32, 255), (16, 17), (0, 1, 255)):
        states = []
        for cpu in (old, new):
            for address, value in ((0x6f1d, hurt), (0x6f1c, kind), (0xdc, pad),
                                   (0x6002, selected), (0x7d8c, 32), (0x7d8d, 85),
                                   (0x7d9e, hud), (0x146, 255), (0x7d8e, 255)):
                cpu.memory[address] = value
            cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0xa6f2, 83, 71, 109, 0x61, 224
            cpu.stPushWord(0x5aff)
            for _ in range(100):
                if cpu.pc == 0x5b00:
                    break
                cpu.step()
            else:
                raise AssertionError('Native inventory leaf did not return')
            states.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp,
                           tuple(cpu.memory[a] for a in (0x7d8c, 0x7d8d, 0x7d9e, 0x146, 0x7d8e))))
        assert states[0] == states[1], (hurt, kind, pad, selected, hud, states)
        checks += 1
    return dict(classification_pairs=classifier, native_leaf_pairs=checks)


def gameplay(trial, linked):
    m = C.menu(trial, 1, {'images': {}})
    symbols = linked['pause']['symbols']
    fields = linked['fields']
    totals = Counter()
    def frame(pad):
        m.controller_pad = pad
        def observe(memory, cpu):
            if memory.rawtags[1] == 3 and cpu.pc in (symbols['PauseWeapons'], symbols['ResetWeapons'],
                                                    linked['alternate']['symbols']['PausedSelect']):
                totals[{symbols['PauseWeapons']: 'pause_tick', symbols['ResetWeapons']: 'weapon_reset',
                        linked['alternate']['symbols']['PausedSelect']: 'select_leaf'}[cpu.pc]] += 1
        C.Game.frame(m, observe)
    def value(address):
        return m.ram[2][address-0xc000]
    for _ in range(650):
        frame(0)
        if value(PRIVATE['WeaponReady']):
            break
    else:
        raise AssertionError(('Native UI did not initialize Jay weapons', dict(totals)))
    assert (value(0xc0be), value(0xc0bf), value(fields[0xb8])) == (63, 2, 0)
    frame(32)
    assert value(fields[0xb8]) == 0 and not totals['select_leaf']
    frame(16 | 32)
    assert N.get(m, 'GamePauseStatus') & 1
    assert value(fields[0xb8]) == 0 and not totals['select_leaf']
    actor_fields = tuple(i for i in range(0x10, 0x33) if i != fields[0xb8]-0xc000)
    before = bytes(m.ram[2][i] for i in actor_fields)
    frame(0)
    frame(32)
    assert value(fields[0xb8]) == 2
    for _ in range(12):
        frame(32)
    after = bytes(m.ram[2][i] for i in actor_fields)
    assert value(fields[0xb8]) == 2 and after == before, (value(fields[0xb8]), before.hex(), after.hex(), dict(totals))
    frame(0)
    frame(32)
    assert value(fields[0xb8]) == 0, (value(fields[0xb8]), value(PRIVATE['PreviousSelect']),
        value(PRIVATE['SelectEdge']), N.get(m, 'GamePauseStatus'), N.get(m, 'SavedJoypadBits'), dict(totals))
    frame(0)
    frame(32)
    assert value(fields[0xb8]) == 2
    frame(0)
    for _ in range(60):
        frame(0)
        if not N.get(m, 'GamePauseTimer') and not N.get(m, 'GamePauseStatus') & 0x80:
            break
    frame(16)
    assert not N.get(m, 'GamePauseStatus') & 1
    frame(0)
    frame(64)
    assert value(0xc0be) == 61
    first_rounds = [T.Weapon.F.slot(m, slot) for slot in T.Weapon.SLOTS]
    assert all(row[9] for row in first_rounds)
    assert [(row[4], row[5]) for row in first_rounds] == [(80, 0), (72, 230), (72, 26)]
    for _ in range(10):
        frame(64)
    assert value(0xc0be) == 61
    assert N.get(m, 'NumberofLives') == 2
    assert (totals['weapon_reset'], totals['select_leaf']) == (1, 3)
    return dict(totals, ammo=value(0xc0be), selection=value(fields[0xb8]), lives=2,
                paused_actor_frozen=True, held_Select_no_repeat=True, held_B_no_repeat=True,
                active_Select_and_held_pause_ingress_ignored=True)


def main():
    raw = H.ROM.read_bytes()
    image, linked = proposal(raw)
    print('Resident/source sizes', linked['pause']['used'], flush=True)
    print('Exact UI parity', isolated_parity(raw, linked['pause']), flush=True)
    trial = dict(W.Symbols.bundle(), raw=image)
    print('Native cold', T.cold_checks(trial, linked), flush=True)
    print('Mike and Steve parity', C.family_parity(dict(trial, raw=raw), trial, None, None, None), flush=True)
    print(json.dumps(dict(passed=True, SHA256=T.digest(image), native=gameplay(trial, linked),
                          output_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
