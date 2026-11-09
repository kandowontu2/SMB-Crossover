"""Read-only c8bd frontend and resident ownership audit for a Simon alternate."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import audit_bub_menu_frontend_1102_v1 as F
import check_hogan_current_bounded_v1 as N
from inventory_playable_menu_1101_v3 import menu_name
from prepare_kirby_first_inhale_1110 import AUTHORITY, R, address, scoped_load


ROM = R / 'build/mini-contact-platform-combo-native-1110/candidate.nes'
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
FAMILY = R / 'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
CYCLE = bytes.fromhex('ade75f6900c9059002a9008de75f8ad0de')
START = bytes.fromhex('0848e005d00cade75fc904d005a92a8d026068284c6fb4')


def off(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def merge(base, extra, label):
    mapping = {key: label + key for key in extra['segs']}
    for key, seg in extra['segs'].items():
        base['segs'][mapping[key]] = seg
    for key, sym in extra['syms'].items():
        row = dict(sym)
        if 'seg' in row:
            row['seg'] = mapping[row['seg']]
        elif key in base['syms'] and 'seg' in base['syms'][key]:
            continue
        base['syms'][key] = row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = ROM.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    b = scoped_load(AUTHORITY)
    merge(b, scoped_load(FAMILY), 'family')
    merge(b, scoped_load(ROM), 'current')
    b['raw'] = raw
    assert address(b, 'Cv3Variant') == 0x5fe7
    reader_rows = dict(names=Counter(), tiles=Counter())
    simon_select = Counter()
    start_ingress = Counter()
    mapped = Counter()

    def watch(c):
        if c.pc < 0x8000:
            return
        m = c.memory
        bank = m.rawtags[(c.pc - 0x8000) // 8192] & 127
        if bank == 66 and c.pc == 0xa975:
            simon_select[(m[0x7309], m[0x6002], m[0x5fe7], c.x, c.p & 1)] += 1
        if bank == 29 and c.pc == 0xb97c:
            start_ingress[(m[0x7309], c.x)] += 1
        if bank == 76 and c.pc == 0xbbcf:
            assert m[c.pc:c.pc + 2] == [0xb1, 5]
            at = m[5] + 256 * m[6] + c.y
            reader_rows['names'][(at - 0xbced) // 16] += 1
        if bank == 76 and c.pc == 0xbc63:
            assert m[c.pc:c.pc + 3] == [0xb9, 0xfd, 0xbe]
            reader_rows['tiles'][c.y // 4] += 1
        if (bank, c.pc) in {(66, 0xaa2f), (76, 0xba6a), (81, 0xbe76), (124, 0xac35), (124, 0xadee)}:
            if m[0x7309] == 5:
                mapped[(bank, c.pc)] += 1

    def call(m, name):
        return F.invoke(m, name, watch=watch)

    def press(m, keys):
        N.put(m, VRAM_Buffer1_Offset=0, CrossoverMenuButtons=0,
              SavedJoypad1Bits=keys, SavedJoypad2Bits=0)
        call(m, 'CrossoverMenuInput')

    named = []
    simon = []
    for slot in range(32):
        m = N.fresh(b)
        N.put(m, CrossoverMenuIndex=slot, CmActive=0)
        m[0x5ffe] = 0
        call(m, 'MenuResolveCharacter')
        call(m, 'QueueSelection')
        seen = set()
        for _ in range(32):
            name, cells = menu_name(m)
            owner = m[0x6002]
            sig = (owner, tuple(cells), bytes(m[0x5fe0:0x5fff]), m[0x730a])
            if sig in seen:
                break
            seen.add(sig)
            named.append((slot, owner, name))
            for key in (16, 48, 128, 160, 176):
                z = N.fork(m)
                press(z, key)
                if slot == 5:
                    simon.append(dict(name=name, before_variant=m[0x5fe7], key=key, after_variant=z[0x5fe7],
                                      final_raw=z[0x6002], final_menu=z[0x7307]))
            press(m, 32)
        else:
            raise AssertionError(('Menu cycle cap', slot))
    profiles = list(dict.fromkeys(row for row in named if row[0] == 5))
    assert profiles == [(5, 5, name) for name in ('SIMON BELMONT', 'GRANT', 'SYPHA', 'ALUCARD')], profiles
    assert all(r[1] != 42 for r in named)
    assert simon_select and all(slot == rawid == x == 5 and carry == 1 for slot, rawid, _, x, carry in simon_select)
    assert start_ingress and all((slot == 5) == (x == 5) for slot, x in start_ingress), start_ingress

    spans = {}
    for label, bank, lo, hi in (
        ('Simon legacy selector', 66, 0xa967, 0xa986),
        ('Menu route selector ingress', 66, 0xa85c, 0xa876),
        ('Mini/Bub toggle exact envelope', 66, 0xb02e, 0xb07c),
        ('QueueSelection', 66, 0xaa51, 0xaa54),
        ('Current Mini stomp takes old DK proposal pad', 66, 0xb58c, 0xb5a7),
        ('Family raw resolver', 76, 0xba6a, 0xba8a),
        ('Family pending entry', 76, 0xb979, 0xb97c),
        ('Family pending foreign tail', 76, 0xbd06, 0xbd0d),
        ('Family static name row10', 76, 0xbd8d, 0xbd9d),
        ('Family static tile row10', 76, 0xbf25, 0xbf29),
        ('Family static palette row10', 76, 0xbf9f, 0xbfa2),
        ('Unused static name row17 in current 32-slot replay', 76, 0xbdfd, 0xbe0d),
        ('Readiness', 76, 0xbff3, 0xc000),
        ('Start retirement redirect and source-declared tail', 29, 0xb97c, 0xb993),
        ('Base resolve slot→raw', 81, 0xbe76, 0xbe9e),
        ('Owner scene gate', 65, 0xb013, 0xb026),
        ('Owner public range gate', 65, 0xa740, 0xa75a),
        ('Cold/check selectors', 65, 0xaee2, 0xaf27),
        ('Shared worker, cookie and pointer arrays', 65, 0xab72, 0xabd4),
        ('Common map helper plus Mini descriptor', 123, 0xb9d6, 0xba00),
        ('Rare private owner classifier', 124, 0xa7ca, 0xa7d9),
        ('Classic menu slot table', 124, 0xa040, 0xa060),
    ):
        at = off(bank, lo)
        spans[label] = dict(bank=bank, CPU_half_open=[lo, hi], file_offset=at,
                            preimage=raw[at:at + hi - lo].hex())
    assert raw[off(29, 0xb97c):off(29, 0xb993)] == bytes.fromhex('4c6fb4') + bytes([0xea]) * 20
    assert raw[off(66, 0xa964):off(66, 0xa967)] == bytes.fromhex('4c14aa')
    assert len(CYCLE) == 17 and len(START) == 23

    def trial(bank, pc, code, stop, variant, x, status):
        m = [0] * 65536
        m[0xa000:0xc000] = raw[off(bank, 0xa000):off(bank, 0xa000) + 8192]
        m[pc:pc + len(code)] = code
        m[0x5fe7], m[0x7309], m[0x6002] = variant, x, 5
        c = F.NesMPU(memory=m, pc=pc)
        c.a, c.x, c.y, c.p, c.sp = 83, x, 91, status, 224
        for _ in range(30):
            if c.pc == stop:
                return m, c
            c.step()
        raise AssertionError((bank, pc, stop, c.pc))

    for v in range(5):
        m, c = trial(66, 0xa975, CYCLE, 0xaa14, v, 5, 0x31)
        assert (m[0x5fe7], c.a, c.x, c.y, c.sp) == ((v + 1) % 5, 5, 5, 91, 224)
    for x in range(32):
        for v in range(5):
            m, c = trial(29, 0xb97c, START, 0xb46f, v, x, 0xb5)
            assert (m[0x6002], c.a, c.x, c.y, c.p & 0xcf, c.sp) == (42 if x == 5 and v == 4 else 5,
                                                                         83, x, 91, 0x85, 224)

    proof = dict(ROM_sha256=PIN, read_only=True, menu_machine_states=len(named),
                 named_profile_count=len(set(named)), slot5_profiles=profiles, slot5_actual_confirm=simon,
                 slot5_resolve_path=[dict(bank=bank, pc=pc, calls=hits) for (bank, pc), hits in mapped.items()],
                 Simon_A975_ingress=[dict(slot=slot, raw=rawid, variant=variant, X=x, carry=carry, hits=hits)
                                     for (slot, rawid, variant, x, carry), hits in sorted(simon_select.items())],
                 Start_B97C_ingress=[dict(slot=slot, X=x, hits=hits) for (slot, x), hits in sorted(start_ingress.items())],
                 isolated_unapplied_leaf_measurement=dict(
                     cycle=dict(bank=66, pc=0xa975, bytes=CYCLE.hex(), legal_states=5, assumes_existing_raw5_menu=True),
                     confirmation=dict(bank=29, pc=0xb97c, bytes=START.hex(), inputs=160,
                                       must_pass_FmPlayable_and_have_raw42_backend_first=True)),
                 static_actual_reader_rows=reader_rows, exact_preimages=spans)
    args.output.mkdir(exist_ok=True)
    (args.output / 'audit.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(slot5_profiles=profiles, static_actual_reader_rows=reader_rows,
                          Simon_A975_ingress=proof['Simon_A975_ingress'])))


if __name__ == '__main__':
    main()
