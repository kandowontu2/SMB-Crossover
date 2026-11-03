"""Finite current-Mini DK Jr readiness and source-funded navigation study.

Never emits a ROM or admits a profile. Frozen v7/v10 are read-only inputs.
The only proposed bytes are arithmetic replacements for the existing two
32-byte horizontal tables, their two typed readers, and an optional focused
DK resolver inside that exact recovered span. Mini's resolver is retained.
"""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, re, subprocess, sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools/reference')]
import audit_current_menu_indicators_1102_v1 as A
import audit_bub_menu_frontend_1102_v1 as F
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address, location
from inventory_playable_menu_1101_v3 import menu_name

ROM = R / 'build/mini-mario-end-candidate-root-1103-v49/mini-end.nes'
PIN = 'ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'
O = R / 'build/dkjr-menu-ca90-1103-v11'
OLD = R / 'build/dkjr-menu-current-1103-v1'
sha = lambda b: hashlib.sha256(b).hexdigest()
off = lambda bank, pc: 16 + bank * 8192 + pc - 0xa000


def bundle():
    # Reuse existing linked symbols read-only. No dependency restoration,
    # archive extraction, source build, or debug-tree copy is performed.
    b = A.bundle()
    b['raw'] = ROM.read_bytes()
    assert sha(b['raw']) == PIN
    return b


def view(m):
    return (tuple(bytes(v) for v in m.ram), bytes(m[:256]),
            bytes(m[0x200:0x800]), bytes(m[0x15a:0x17b]),
            bytes(m[0x5fe0:0x8000]), tuple(m.rawtags),
            tuple(m.ppu_log), tuple(m.chr_latches), m.upper, m.lastset)


def key(m, value, pad=1, p=0x31):
    N.put(m, VRAM_Buffer1_Offset=0, CrossoverMenuButtons=0,
          SavedJoypad1Bits=value if pad == 1 else 0,
          SavedJoypad2Bits=value if pad == 2 else 0)
    return F.invoke(m, 'CrossoverMenuInput', p=p)


def seed(b, slot):
    m = N.fresh(b)
    N.put(m, CrossoverMenuIndex=slot, CmActive=0)
    m[0x5ffe] = 0
    F.invoke(m, 'MenuResolveCharacter')
    F.invoke(m, 'QueueSelection')
    return m


def readiness(b):
    raw = b['raw']
    proposal = json.loads((OLD / 'current-menu-v7.json').read_text())
    assert sha((OLD / 'current-menu-v7.json').read_bytes()) == 'a40b5d4dd0d0af1a92b652a5ed2d4bcdc9bfad6026d3889b1e8fb68419b4b829'
    conflicts = []
    for i, row in enumerate(proposal['proposed_patch_list']):
        at = row['file_offset']; old = bytes.fromhex(row['old_hex'])
        actual = raw[at:at + len(old)]
        conflicts.append(dict(index=i, physical_PRG=row['physical_PRG'],
                              CPU_half_open=row['CPU_half_open'], bytes=len(old),
                              old_preimage_matches=actual == old,
                              different_bytes=sum(x != y for x, y in zip(old, actual)),
                              current_SHA256=sha(actual)))
    donor_path = Path('C:/NES/Donkey Kong Jr. (World) (Rev 1).nes')
    donor = donor_path.read_bytes()
    assert sha(donor) == '1bc7fdc98c29b2c51438c3ce92ca37fac61b939a7cf100c644fed37206cf2cf6'
    portrait = donor[16400 + 1280:16400 + 1408]
    assert raw[1048592 + 960 * 1024 + 256:1048592 + 960 * 1024 + 384] == portrait
    scene = raw[off(65, 0xb013):off(65, 0xb026)]
    assert scene.startswith(bytes.fromhex('0848ad026038e925c905'))
    manager_source = R / 'build/mini-mario-owner-1103-v15/owner-final-v19.s'
    assert ' cmp #5\n bcs CoSelectNo' in manager_source.read_text()
    grants = json.loads((R / 'docs/qa/allocations/prince-current-frontend-1103-v105.json').read_text())
    prince = []
    for row in grants['approved_exact_patches']:
        at = row['file_offset']; old = bytes.fromhex(row['old_hex']); new = bytes.fromhex(row['new_hex'])
        assert raw[at:at + len(old)] in (old, new)
        prince.append(dict(file_offset=at, bytes=len(old),
                           current_is_approved_final=raw[at:at + len(old)] == new))
    return dict(parent_SHA256=PIN, frozen_v7_preimages=conflicts,
                old_v7_preimages_matching=sum(p['old_preimage_matches'] for p in conflicts),
                old_v7_preimages_total=len(conflicts), original_idle_portrait=dict(
                    physical_CHR=960, byte_half_open=[256, 384], bytes=128,
                    SHA256=sha(portrait), exact_original=True),
                existing_scene_gate=dict(physical_PRG=65, CPU_half_open=[0xb013, 0xb026],
                                         bytes_hex=scene.hex(), legal_owners=[37, 38, 39, 40, 41],
                                         no_old_cmp3_to4_patch_needed=True),
                Prince105_disjoint_layer=prince,
                blockers=['Frozen v7 cannot rebase: Mini owns its previous nav/gate/code/data extents.',
                          'A combined fresh Select28/40 toggle and static name/colored-preview leaf are still required.',
                          'The focused resolver measured here is not a complete menu admission.',
                          'New menu IRQ/FF/CHR-publication/native tests remain after exact composition review.'])


SOURCE = '''.setcpu "6502"
.segment "NAV_FACTOR"
.export Left,Right,FocusedResolve,UsedEnd,FreeStart
Left:
 php
 txa
 and #7
 bne Decrement
 txa
 ora #7
 bne Return
Decrement:
 dex
 txa
 inx
Return:
 plp
 ora #0
 rts
Right:
 php
 inx
 txa
 and #7
 beq Wrap
 txa
 dex
 jmp Return
Wrap:
 dex
 txa
 and #24
 jmp Return
FocusedResolve:
 php
 cpx #27
 bne Old
 lda $6002
 cmp #40
 bne Old
 plp
 lda #40
 rts
Old:
 plp
 jmp $a0a1
FreeStart:
 .res $40-(*-Left),$ea
UsedEnd:
'''


def factor(b):
    old = b['raw']; p = O / 'horizontal-factor'
    p.with_suffix('.s').write_text(SOURCE)
    cfg = 'MEMORY{P:start=$a000,size=$40,file=%O;}SEGMENTS{NAV_FACTOR:load=P,type=ro;}'
    p.with_suffix('.cfg').write_text(cfg)
    cc = R / 'tools/Windows/cc65/bin'
    for cmd in [[cc / 'ca65.exe', p.with_suffix('.s'), '-o', p.with_suffix('.o')],
                [cc / 'ld65.exe', '-C', p.with_suffix('.cfg'), p.with_suffix('.o'),
                 '-o', p.with_suffix('.bin'), '-Ln', p.with_suffix('.lbl')]]:
        z = subprocess.run(list(map(str, cmd)), capture_output=True, text=True)
        assert z.returncode == 0, z.stderr
    p.with_suffix('.o').unlink()
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', p.with_suffix('.lbl').read_text(), re.M)}
    body = p.with_suffix('.bin').read_bytes(); assert len(body) == 64
    assert old[off(124, 0xa000):off(124, 0xa020)] == bytes(i // 8 * 8 + (i - 1) % 8 for i in range(32))
    assert old[off(124, 0xa020):off(124, 0xa040)] == bytes(i // 8 * 8 + (i + 1) % 8 for i in range(32))
    assert old[off(124, 0xadee):off(124, 0xadf1)] == bytes.fromhex('4ca1a0')
    raw = bytearray(old); patches = []
    def put(bank, pc, data, role):
        at = off(bank, pc); before = old[at:at + len(data)]
        raw[at:at + len(data)] = data
        patches.append(dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(data)],
                            file_offset=at, old_hex=before.hex(), new_hex=data.hex(), role=role))
    put(124, 0xa000, body, 'Two source-owned32B horizontal tables become exact arithmetic plus focused-only resolver; all Mini nav fromA040 onward stays exact')
    start = location(b, 'NrMenuNavigate'); end = location(b, 'NrQueueCursor')
    for name, target in [('Left', 0xa000), ('Right', 0xa020)]:
        pattern = bytes([0xbd, target & 255, target >> 8]); assert old.count(pattern, start, end) == 1
        at = old.index(pattern, start, end); assert (at - 16) // 8192 == 124
        put(124, 0xa000 + (at - 16) % 8192,
            bytes([0x20, labels[name] & 255, labels[name] >> 8]),
            'Typed LDA table,X -> JSR arithmetic; X/Y and C/V/D/I preserved, NZ reflect returnedA')
    put(124, 0xadee, bytes([0x4c, labels['FocusedResolve'] & 255, labels['FocusedResolve'] >> 8]),
        'Public AltTail onlyJMP; originalMini resolverA0A1 and14B coldclear remain exact')
    for row in json.loads((R / 'docs/qa/allocations/prince-current-frontend-1103-v105.json').read_text())['approved_exact_patches']:
        at = row['file_offset']; n = len(bytes.fromhex(row['old_hex']))
        assert raw[at:at + n] == old[at:at + n], 'Prince source extent changed'
    assert raw[off(124, 0xa040):off(124, 0xa0e0)] == old[off(124, 0xa040):off(124, 0xa0e0)]
    assert raw[off(124, 0xadf1):off(124, 0xadff)] == old[off(124, 0xadf1):off(124, 0xadff)]
    assert raw[off(65, 0xa000):off(65, 0xc000)] == old[off(65, 0xa000):off(65, 0xc000)]
    return dict(b, raw=bytes(raw)), dict(labels=labels, patches=patches,
        horizontal_code_bytes=labels['FocusedResolve'] - 0xa000,
        focused_resolver_bytes=labels['FreeStart'] - labels['FocusedResolve'],
        remaining_source_owned_bytes=0xa040 - labels['FreeStart'],
        expected_memory_only_SHA256=sha(raw), ROM_written=False,
        Mini_A040_A0E0_and_Cold14_exact=True, all_PRG65_five_owner_bytes_exact=True,
        retained_prototype_negative=dict(slot=0, pressed=1, expected_A=1,
            actual_A=24, actual_X=255,
            cause='BNE after DEX consumed restoredX zero flag rather than resultA; replaced with unconditionalJMP before qualification'))


def qualify(old, new):
    counts = collections.Counter(); points = collections.Counter(); rows = []
    flags = [0x30, 0x31, 0x70, 0xf1]
    seeds = [N.fresh(b) for b in [old, new]]
    for slot, p, mask in itertools.product(range(32), flags, [0, 1, 2, 4, 8, 15]):
        pair = []
        for initial in seeds:
            m = N.fork(initial); N.put(m, CrossoverMenuIndex=slot, CrossoverMenuPressed=mask, VRAM_Buffer1_Offset=0)
            pair.append((m, F.invoke(m, 'NrMenuNavigate', p=p)))
        a, za = pair[0]; b, zb = pair[1]
        assert all(za[k] == zb[k] for k in ['A', 'X', 'Y', 'P']) and view(a) == view(b), ('navigation', slot, p, mask, za, zb)
        counts['navigation_AXYP_full_state'] += 1
    # Actual original public resolver X domain, preserving all private Mini
    # and foreign states. Name/PPU/OAM are compared, not only final rawID.
    fields = sorted(n for n, s in old['syms'].items() if 'Variant' in n and '::' not in n and not n.startswith('.') and 0 <= int(s['val'], 0) < 0x8000)
    for slot in range(32):
        pair = [seed(b, slot) for b in [old, new]]; seen = set()
        for cycle in range(24):
            a, b = pair; name, cells = menu_name(a)
            sig = (name, N.get(a, 'SelectedCharacter'), a[0x5ffe], a[0x5fe5], a[0x5fe8], tuple(N.get(a, n) for n in fields))
            if sig in seen: break
            seen.add(sig); assert view(a) == view(b), ('profile', slot, cycle, name)
            rows.append(dict(slot=slot, cycle=cycle, name=name, raw=N.get(a, 'SelectedCharacter'), MarioVariant=N.get(a, 'MarioVariant')))
            for pad, value in itertools.product([1, 2], [16, 128, 48, 160]):
                trial = [N.fork(m) for m in pair]; z = [key(m, value, pad) for m in trial]
                assert z[0] == z[1] and view(trial[0]) == view(trial[1]), ('confirm', slot, name, pad, value)
                counts['legacy_P1_P2_Start_A_Select_confirm'] += 1
            for m in pair: key(m, 32)
        else: raise AssertionError(('unbounded legal family', slot))
    # Distinct Jr focus test deliberately checks only resolver identity. The
    # existing DK name remains DK until a future source-funded UI leaf exists.
    own = []
    for p, x, y in itertools.product(flags, [27], [0, 91, 255]):
        m = N.fork(seeds[1]); N.put(m, CrossoverMenuIndex=27, SelectedCharacter=40)
        z = F.invoke(m, 'NrMenuCharacter', a=83, x=x, y=y, p=p)
        assert z['A'] == 40 and z['X'] == x and z['Y'] == y
        own.append(z)
    for slot in range(32):
        pair = [N.fork(m) for m in seeds]
        for m in pair: N.put(m, CrossoverMenuState=1, CrossoverMenuIndex=slot, Mirror_PPUMASK=0, DisableScreenFlag=1, VRAM_Buffer1_Offset=0)
        z = [F.invoke(m, 'CrossoverMenuInput') for m in pair]
        assert z[0] == z[1] and view(pair[0]) == view(pair[1]) and pair[0].vram == pair[1].vram
        counts['actual_32_screen_constructors'] += 1
    assert any(r['raw'] == 41 and r['name'] == 'MINI MARIO' for r in rows)
    assert any(r['name'] == 'BUB' for r in rows) and any(r['name'] == 'BOB' for r in rows)
    assert not any(r['raw'] == 40 for r in rows), 'Study must not claim Select admission'
    return dict(passed=True, CPU_only=True, checks=dict(counts), rows=rows,
                legacy_machine_states=len(rows), distinct_named_profiles=len({(r['slot'], r['name']) for r in rows}),
                Jr_focused_resolver_cases=len(own), Jr_actual_Select_admitted=False,
                no_native_or_interrupt_qualification_claim=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--readiness-only', action='store_true'); args = ap.parse_args()
    O.mkdir(exist_ok=True)
    b = bundle(); out = readiness(b)
    if not args.readiness_only:
        new, measure = factor(b)
        out['source_funding_measurement'] = measure
        out['CPU'] = qualify(b, new)
    out.update(passed=True, status='SOURCE_ONLY_PARTIAL_FUNDING_NOT_ADMITTED', ROM_written=False,
               menu_admitted=False, native_qualified=False, task_root=O.relative_to(R).as_posix(),
               source_files_to_commit=[Path(__file__).relative_to(R).as_posix()],
               bindings={p.relative_to(R).as_posix(): sha(p.read_bytes()) for p in [Path(__file__), ROM,
                   OLD / 'current-menu-v7.json', OLD / 'current-menu-rebase-v10.json',
                   R / 'build/mini-mario-menu-1103-v14/proposal-v16.json',
                   R / 'docs/qa/allocations/prince-current-frontend-1103-v105.json']})
    (O / 'readiness-v11.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k in ['passed', 'status', 'old_v7_preimages_matching', 'old_v7_preimages_total', 'source_funding_measurement']}))


if __name__ == '__main__':
    main()
