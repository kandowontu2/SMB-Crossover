"""Fit a 33rd roster position in the existing navigation-table allocation.

CPU-only proposal: no ROM output, menu admission, shared source edit or install.
The new family still needs its real resolver, portrait and native lifecycle.
"""
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
import check_hogan_current_bounded_v1 as M

O = R / 'build/bub-menu-navigation-1102-v1'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def snapshot(m):
    return (bytes(m[:256]), bytes(m[0x200:0x800]), bytes(m[0x5c00:0x8000]),
            tuple(bytes(v) for v in m.ram), tuple(m.rawtags),
            bytes(m[0x15a:0x17b]), tuple(m.chr_latches), m.upper, m.lastset)


def cursor(i):
    return 0x2000 + (5 + 4 * (i // 8)) * 32 + 3 + 3 * (i % 8)


def directions(i):
    if i == 32:
        return dict(Left=32, Right=32, Up=24, Down=0)
    row = i // 8 * 8
    return dict(Left=row + (i - 1) % 8, Right=row + (i + 1) % 8,
                Up=32 if i < 8 else i - 8,
                Down=32 if i >= 24 else i + 8)


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    old = scoped_load(ROM)
    origin = location(old, 'X5MenuLeft')
    assert origin == 16 + 124 * 8192
    names = ['Left', 'Right', 'Up', 'Down', 'Characters', 'CursorLo', 'CursorHi']
    for i, name in enumerate(names):
        assert address(old, 'X5Menu' + name) == 0xa000 + 32 * i
        assert location(old, 'X5Menu' + name) == origin + 32 * i
    old_tables = {name: list(old['raw'][origin + 32 * i:origin + 32 * (i + 1)])
                  for i, name in enumerate(names)}
    for i in range(32):
        assert old_tables['CursorLo'][i] + 256 * old_tables['CursorHi'][i] == cursor(i)
    tables = {name: [directions(i)[name] for i in range(33)] for name in names[:4]}
    tables['Characters'] = old_tables['Characters'] + [39]
    tables['CursorLo'] = [cursor(i) & 255 for i in range(33)]
    source = '.setcpu "6502"\n.segment "BUB_MENU_NAV"\n'
    for name, values in tables.items():
        source += f'.export BubMenu{name}\nBubMenu{name}:\n .byte ' + ','.join(map(str, values)) + '\n'
    source += '''.export BubMenuCursorHi,BubMenuUsedEnd
BubMenuCursorHi:
 php
 tya
 lsr
 lsr
 lsr
 clc
 adc #1
 lsr
 clc
 adc #$20
 plp
 ora #0
 rts
BubMenuUsedEnd:
 .res $e0-(*-BubMenuLeft),$ff
'''
    (O / 'navigation.s').write_text(source, encoding='utf-8')
    (O / 'navigation.cfg').write_text(
        'MEMORY{P:start=$a000,size=$e0,file=%O;}SEGMENTS{BUB_MENU_NAV:load=P,type=ro;}', encoding='utf-8')
    cc = R / 'tools/Windows/cc65/bin'
    for cmd in [[cc / 'ca65.exe', O / 'navigation.s', '-o', O / 'navigation.o'],
                [cc / 'ld65.exe', '-C', O / 'navigation.cfg', O / 'navigation.o',
                 '-o', O / 'navigation.bin', '-Ln', O / 'navigation.lbl']]:
        p = subprocess.run(list(map(str, cmd)), capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
    import re
    lab = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                (O / 'navigation.lbl').read_text(), re.M)}
    body = (O / 'navigation.bin').read_bytes()
    assert len(body) == 224 and lab['BubMenuUsedEnd'] == 0xa0d6
    new = copy.deepcopy(old)
    raw = bytearray(old['raw'])
    raw[origin:origin + 224] = body
    patches = []
    def operand(function, size, name, opcode):
        at = location(old, function)
        pc = address(old, 'X5Menu' + name)
        pattern = bytes([opcode, pc & 255, pc >> 8])
        assert raw.count(pattern, at, at + size) == 1, (function, name)
        offset = raw.index(pattern, at, at + size)
        target = lab['BubMenu' + name]
        replacement = bytes([0x20 if name == 'CursorHi' else opcode, target & 255, target >> 8])
        patches.append(dict(function=function, table=name, offset=offset,
                            old=pattern.hex(), new=replacement.hex()))
        raw[offset:offset + 3] = replacement
    for name in names[:4]:
        operand('NrMenuNavigate', address(old, 'NrQueueCursor') - address(old, 'NrMenuNavigate'), name, 0xbd)
    assert old['raw'][location(old, 'NrMenuCharacter'):location(old, 'NrMenuCharacter') + 3] == bytes.fromhex('4ceead')
    operand('NrMenuAltTail', 17, 'Characters', 0xbd)
    operand('NrQueueCursor', 42, 'CursorLo', 0xb9)
    operand('NrQueueCursor', 42, 'CursorHi', 0xb9)
    new['raw'] = bytes(raw)

    # Current expanded QueueCursor is an unconditional tail-call thunk. The
    # following legacy body and both twelve-byte tables have no legal entry.
    qs = location(old, 'QueueCursor')
    qc = address(old, 'NrQueueCursor')
    thunk = bytes.fromhex('8d6a01a9') + bytes([qc & 255]) + bytes.fromhex('8d6c01a9') + bytes([qc >> 8]) + bytes.fromhex('8d6d01a9fc4c5a01')
    assert old['raw'][qs:qs + 18] == thunk
    assert address(old, 'CursorLow') == 0xad63 and address(old, 'CursorHigh') == 0xad6f
    assert address(old, 'QueueTitleCursor') == 0xad7b
    assert old['raw'][qs + 18:qs + 60] == bytes.fromhex(
        '48ac0973b9a0a0aeae049db004b9c0a09daf04a9019db104689db2048a186904aa8eae04a9009daf046060')[:42]

    seeds = [M.fresh(b) for b in [old, new]]
    cursor_cases = navigation_cases = character_cases = 0
    for index in range(33):
        for flags in [0x30, 0x31, 0x70, 0xf1]:
            for offset in [0, 32, 76]:
                pair = []
                for seed in seeds:
                    m = M.fork(seed)
                    M.put(m, CrossoverMenuIndex=index, VRAM_Buffer1_Offset=offset)
                    at = address(m.bundle, 'VRAM_Buffer1')
                    m[at:at + 85] = bytes([0xa5]) * 85
                    z = M.invoke(m, 'QueueCursor', a=253, x=7, y=91, p=flags)
                    pair.append((m, z))
                m, z = pair[1]
                pos = cursor(index)
                assert bytes(m[at + offset:at + offset + 5]) == bytes([pos >> 8, pos & 255, 1, 253, 0])
                assert M.get(m, 'VRAM_Buffer1_Offset') == offset + 4
                if index < 32:
                    assert snapshot(pair[0][0]) == snapshot(m), ('cursor ABI state', index, flags, offset)
                    assert all(pair[0][1][k] == z[k] for k in ['A', 'X', 'Y', 'P']), ('cursor registers', index, flags)
                    assert z['minimum_SP'] >= pair[0][1]['minimum_SP'] - 3
                cursor_cases += 1
            for mask in [0, 1, 2, 4, 8, 15]:
                m = M.fork(seeds[1])
                M.put(m, CrossoverMenuIndex=index, CrossoverMenuPressed=mask, VRAM_Buffer1_Offset=0)
                z = M.invoke(m, 'NrMenuNavigate', p=flags)
                key = 'Up' if mask & 8 else 'Down' if mask & 4 else 'Left' if mask & 2 else 'Right'
                assert z['A'] == (directions(index)[key] if mask else 255), ('navigation', index, mask, z['A'])
                assert M.get(m, 'CrossoverMenuIndex') == index
                navigation_cases += 1
        # No menu-resolution or gameplay call is made for raw39 here.
        m = M.fork(seeds[1])
        z = M.invoke(m, 'NrMenuCharacter', x=index)
        # Current NrMenuCharacter includes existing special-family handling;
        # its direct table result applies to the proposed plain family only.
        if index == 32:
            assert z['A'] == 39
        character_cases += 1
    q = dict(passed=True, ROM_sha256=PIN, proposal_only=True, ROM_written=False,
             menu_admitted=False, native_playable=False, slots=33, table_allocation_bytes=224,
             used_bytes=214, spare_bytes=10, patches=patches,
             cursor_full_thunk_cases=cursor_cases, actual_navigation_cases=navigation_cases,
             actual_character_table_cases=character_cases,
             new_slot=dict(index=32, proposed_raw_ID=39, icon_left_X=32, icon_top_Y=160,
                           cursor_nametable_address=cursor(32), overlaps_center_preview=False),
             front_end_dead_span_proposal=dict(physical_PRG_bank=66, CPU_half_open=[0xad39, 0xad7b],
                 bytes=66, expanded_thunk_never_falls_through=True, granted=False,
                 preimage_SHA256=hashlib.sha256(old['raw'][qs + 18:qs + 84]).hexdigest(),
                 remaining='Root must review all named/source readers before granting; no routine may enter a retired label.'),
             remaining=['Real Bub/Bob resolver, Select selector, name/portrait and BG silhouette are not implemented.',
                        'Actual native loader/services and owner-specific enemy hooks must pass before confirmation.'],
             bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), ROM,
                        R / 'src/character_select.s', R / 'src/new_roster_dispatch.s']})
    (O / 'proposal.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in q.items() if k not in ['bindings', 'patches']}))


if __name__ == '__main__':
    main()
