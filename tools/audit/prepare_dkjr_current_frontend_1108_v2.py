"""Propose a focused DK Jr menu alternate on the installed 244734 bytes.

All cartridge changes are in memory. The private proposal shares the existing
DK family portrait. It adds no RAM, CHR, gameplay code, or public admission.
"""
from collections import Counter
import argparse
from itertools import product
from pathlib import Path
import json

import audit_dkjr_installed_ingress_1108_v1 as I

R, O, UI, N, F = I.R, I.O, I.UI, I.N, I.F
off, sha = UI.off, I.sha
GRANT = R / 'docs/qa/allocations/prince-current-frontend-1103-v105.json'
NAME = bytes(36 if c == ' ' else ord(c) - 55 for c in ' DONKEY KONG JR ')
PENDING = 0xb979
NAME_COPY = 0xbbcf
TILES_COPY = 0xbc63


def compose(raw):
    image = bytearray(raw)
    patches = []
    owned = set()

    def apply(bank, pc, before, after, role):
        before = bytes.fromhex(before) if isinstance(before, str) else bytes(before)
        after = bytes.fromhex(after) if isinstance(after, str) else bytes(after)
        at = off(bank, pc)
        assert before and len(before) == len(after)
        assert raw[at:at+len(before)] == before, (bank, hex(pc), raw[at:at+len(before)].hex())
        occupied = set(range(at, at + len(before)))
        assert not owned.intersection(occupied)
        owned.update(occupied)
        image[at:at+len(before)] = after
        patches.append(dict(file_offset=at, physical_PRG=bank, CPU_half_open=[pc, pc + len(before)],
                            old_hex=before.hex(), new_hex=after.hex(), role=role))

    prior = json.loads(I.UISTUDY.read_text())['source_funding_measurement']
    for row in prior['patches']:
        apply(row['physical_PRG'], row['CPU_half_open'][0], row['old_hex'], row['new_hex'], row['role'])
    # Current MiniToggle slot split. The new gate rejoins the original
    # variant-7 comparison or the original MR GIMMICK slot comparison.
    apply(66, 0xb038, 'd010ad0a73', '4c92b5eaea', 'MiniToggle slot split only; original Mini and MR GIMMICK leaves remain at their installed addresses')
    assert raw[off(66, 0xb58c):off(66, 0xb592)].hex() == '4cadb54cfabd'
    apply(66, 0xb592, 'ea'*19, 'e01bf00c8ad006ad0a734c3db04c4ab04c97b4',
          'PN variant hint two public JMPs skip this source-declared 21B pad. Route slot27 to DK flip; slot0 restores A=variant; foreign rejoins CPX25.')
    assert raw[off(66, 0xb48a):off(66, 0xb497)].hex() == 'a9c78d4c01a9838de5734c7ab5'
    apply(66, 0xb497, 'ff'*10, 'ad026049348d02603860',
          'Exact HotPlayerGraphics fixed-envelope tail after Mini unconditional JMP; flip coherent focused raw28/40 using XOR34.')
    # Pending describes use of the existing static UI route here. The
    # existing readiness threshold accepts its index17 for Start and A.
    assert raw[off(76, 0xb9f5):off(76, 0xb9f7)] == bytes.fromhex('e01b')
    apply(76, 0xb9f7, 'f0e8', 'f06d', 'Existing DK slot comparison redirects to the same FmPending envelope tail.')
    assert raw[off(76, 0xba62):off(76, 0xba66)].hex() == '18603860'
    apply(76, 0xba66, 'eaeaea', '4c25bf', 'FmPending trailing unreachable pad immediately after both RTS exits.')
    apply(76, 0xbf25, bytes(range(80, 112, 2)), '48ad0260c928d00568a91138604cfbbf',
          'Compiled FmPreviewTiles rows10..13 have no reachable static portrait readers; raw40 returns A17/C1, raw28 falls through exact flags restoration.')
    assert raw[off(76, 0xbff3):off(76, 0xbffb)].hex() == '2079b99002c91960'
    apply(76, 0xbffb, 'ea'*5, '68e01b1860',
          'FmPlayable fixed end-of-bank tail after RTS. Restore the former raw28 A/X/Y/NZ/C/V/D/I behavior.')
    apply(76, 0xbdfd, '24243f0d1817140e2224141817102424', NAME,
          'Unused static FmNames row17; original native raw28 uses the separate DK name source.')
    prince = json.loads(GRANT.read_text())['approved_exact_patches']
    for row in prince:
        at = row['file_offset']; before = bytes.fromhex(row['old_hex']); after = bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(before)] in (before, after)
        assert not owned.intersection(range(at, at+len(before)))
    assert raw[off(65, 0xa000):off(65, 0xc000)] == image[off(65, 0xa000):off(65, 0xc000)]
    assert raw[0x100010:] == image[0x100010:]
    return bytes(image), patches


def axyp(z):
    return tuple(z[k] for k in ('A', 'X', 'Y', 'P'))


def key(m, button, pad=1, watch=None, flags=0x31):
    N.put(m, VRAM_Buffer1_Offset=0, CrossoverMenuButtons=0,
          SavedJoypad1Bits=button if pad == 1 else 0, SavedJoypad2Bits=button if pad == 2 else 0)
    return F.invoke(m, 'CrossoverMenuInput', p=flags, watch=watch)


def qualify(old, new, own_only=False):
    counts = Counter(); profiles = []
    reads = {'old': Counter(), 'new': Counter()}
    retired = ((66, 0xb592, 0xb5a7), (66, 0xb497, 0xb4a4), (76, 0xba66, 0xba6a),
               (76, 0xbf25, 0xbf35), (76, 0xbffb, 0xc000))

    def watch(side):
        def sample(c):
            if c.pc < 0x8000: return
            bank = c.memory.rawtags[(c.pc - 0x8000) // 8192] & 127
            if side == 'old':
                assert not any(bank == b and lo <= c.pc < hi for b, lo, hi in retired), (bank, hex(c.pc))
            if bank != 76: return
            if c.pc == NAME_COPY:
                assert c.memory[c.pc] == 0xb1 and c.memory[c.pc+1] == 5
                effective = c.memory[5] + 256*c.memory[6] + c.y
                reads[side]['name_row_' + str((effective - 0xbced)//16)] += 1
            if c.pc == TILES_COPY:
                assert tuple(c.memory[c.pc:c.pc+3]) == (0xb9, 0xfd, 0xbe)
                reads[side]['tile_row_' + str(c.y//4)] += 1
        return sample

    watches = [watch('old'), watch('new')]
    bundles = [old, new]
    seeds = [N.fresh(b) for b in bundles]
    flags = [0x30, 0x31, 0x70, 0xf1]
    fields = sorted(n for n, s in old['syms'].items() if 'Variant' in n and '::' not in n and not n.startswith('.') and 0 <= int(s['val'], 0) < 0x8000)
    slots = [] if own_only else range(32)
    for slot, p, mask in product(slots, flags, [0, 1, 2, 4, 8, 15]):
        pair = [N.fork(m) for m in seeds]
        for m in pair:
            N.put(m, CrossoverMenuIndex=slot, CrossoverMenuPressed=mask, VRAM_Buffer1_Offset=0)
        z = [F.invoke(m, 'NrMenuNavigate', p=p, watch=w) for m,w in zip(pair,watches)]
        assert axyp(z[0]) == axyp(z[1]) and UI.view(pair[0]) == UI.view(pair[1]), ('navigation',slot,p,mask,z)
        counts['navigation_AXYP_full_state'] += 1
    for slot in slots:
        pair = [N.fork(m) for m in seeds]
        for m in pair:
            N.put(m, CrossoverMenuState=1, CrossoverMenuIndex=slot, Mirror_PPUMASK=0, DisableScreenFlag=1, VRAM_Buffer1_Offset=0)
        z = [F.invoke(m, 'CrossoverMenuInput', watch=w) for m,w in zip(pair,watches)]
        assert z[0] == z[1] and UI.view(pair[0]) == UI.view(pair[1]) and pair[0].vram == pair[1].vram, ('constructor',slot,z)
        counts['constructors_AXYP_SP_full_state_VRAM'] += 1
    for slot in slots:
        pair = [N.fork(m) for m in seeds]; seen = set()
        for m,w in zip(pair,watches):
            N.put(m, CrossoverMenuIndex=slot, CmActive=0)
            m[0x5ffe] = 0
            F.invoke(m, 'MenuResolveCharacter', watch=w)
            F.invoke(m, 'QueueSelection', watch=w)
        for cycle in range(24):
            a,b = pair
            name, tiles = UI.menu_name(a)
            raw = N.get(a,'SelectedCharacter')
            sig = (name, raw, a[0x5ffe], a[0x5fe5], a[0x5fe8], tuple(N.get(a,n) for n in fields))
            if sig in seen: break
            seen.add(sig)
            assert UI.view(a) == UI.view(b), ('profile',slot,cycle,name)
            profiles.append(dict(slot=slot, cycle=cycle, name=name, raw=raw))
            for pad, button in product([1,2], [0,1,2,4,8,16,32,48,64,128,160,176]):
                if slot == 27 and button & 32: continue
                trial = [N.fork(m) for m in pair]
                result = [key(m,button,pad,w) for m,w in zip(trial,watches)]
                assert axyp(result[0]) == axyp(result[1]) and UI.view(trial[0]) == UI.view(trial[1]), ('legacy key',slot,cycle,name,pad,button,result)
                counts['legacy_P1_P2_AXYP_full_state'] += 1
                if result[0]['minimum_SP'] != result[1]['minimum_SP']:
                    counts['legacy_keys_different_min_SP'] += 1
            if slot == 27: break
            for m,w in zip(pair,watches): key(m,32,watch=w)
        else: raise AssertionError(('unbounded legal Select cycle',slot))
    if not own_only:
        assert len(profiles) == 95 and len({(r['slot'],r['name']) for r in profiles}) == 94
        assert any(r['raw'] == 41 and r['name'] == 'MINI MARIO' for r in profiles)
        assert reads['old'] and not reads['old']['name_row_17']
    assert all(not reads['old']['tile_row_'+str(i)] for i in range(10,14))
    assert all(not reads['new']['tile_row_'+str(i)] for i in range(10,14))

    dk = UI.seed(old,27)
    palette = lambda m: [row for row in F.commands(m) if row['address']==0x3f11]
    N.put(dk,VRAM_Buffer1_Offset=0)
    F.invoke(dk,'DrawSelectionPreview',watch=watches[0])
    expected_palette = [dict(address=0x3f11,length=3,bytes=[48,54,6])]
    assert palette(dk) == expected_palette, palette(dk)
    own = []; simultaneous = []
    for pad,p in product([1,2],flags):
        m = UI.seed(new,27)
        z = key(m,32,pad,watches[1],p)
        assert N.get(m,'SelectedCharacter') == 40 and N.get(m,'CrossoverMenuState') == 2
        assert UI.menu_name(m) == ('DONKEY KONG JR',list(NAME)), UI.menu_name(m)
        assert bytes(m[0x200:0x218]) == bytes(dk[0x200:0x218]) and any(x < 240 for x in m[0x200:0x218:4])
        assert palette(m) == palette(dk) and palette(m), (palette(m), palette(dk))
        assert bytes(m[0x730a:0x730b]) == bytes(dk[0x730a:0x730b])
        for button in [16,128]:
            t = N.fork(m); start = key(t,button,pad,watches[1],p)
            assert N.get(t,'SelectedCharacter') == 40 and N.get(t,'CrossoverMenuState') == 0
            own.append(dict(pad=pad, input=button, initial_P=p, result=start))
        t = N.fork(m); key(t,32,pad,watches[1],p)
        assert N.get(t,'SelectedCharacter') == 28 and UI.menu_name(t)[0] == 'DONKEY KONG'
        for button in [48,160]:
            for raw_start in [28,40]:
                t = N.fork(m) if raw_start == 40 else UI.seed(new,27)
                key(t,button,pad,watches[1],p)
                ending = [N.get(t,n) for n in ['CrossoverMenuState','SelectedCharacter']]
                assert ending == [0,raw_start ^ 0x34], (raw_start,button,ending)
                simultaneous.append(dict(pad=pad, initial_P=p, input=button, raw_start=raw_start, result=ending))
        key(m,2,pad,watches[1],p); assert N.get(m,'CrossoverMenuIndex') == 26
        key(m,1,pad,watches[1],p); assert N.get(m,'CrossoverMenuIndex') == 27
        assert N.get(m,'SelectedCharacter') == 28 and UI.menu_name(m)[0] == 'DONKEY KONG'
        counts['focused_Jr_toggles_and_navigation_returns'] += 1
    assert reads['new']['name_row_17'] > 0
    return dict(counts=dict(counts), legacy_machine_states=len(profiles),
                legacy_distinct_profiles=len({(r['slot'],r['name']) for r in profiles}),
                original_table_reads=dict(reads['old']), new_table_reads=dict(reads['new']),
                Jr_P1_P2_Start_A=own, Jr_simultaneous_edges=simultaneous,
                static_DK_family_preview=dict(OAM=list(dk[0x200:0x218]), palette=palette(dk)),
                old_preview_code_name_tables_funding='All actual public legal menu/constructor/navigation keys above; no old execution in repurposed spans, no old name17 or tile rows10..13 fetches.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--own-only',action='store_true',help='Bounded focused diagnostic, with no qualification receipt')
    args = ap.parse_args()
    out = O / 'frontend-v2.json'
    assert not out.exists()
    raw = I.ROM.read_bytes()
    assert sha(raw) == I.PIN
    image, patches = compose(raw)
    print('composed memory only', sha(image), len(patches), flush=True)
    b = I.SYMBOLS.bundle()
    old, new = dict(b,raw=raw), dict(b,raw=image)
    cpu = qualify(old,new,args.own_only)
    if args.own_only:
        print(json.dumps(cpu),flush=True)
        return
    ingress = I.cpu(image, (I.BASE/'native-cookie-v90.bin').read_bytes())
    result = dict(passed=True, source_only=True, ROM_written=False, native_qualified=False,
                  public_admission=False, parent_SHA256=I.PIN, expected_memory_only_SHA256=sha(image),
                  patches=patches, changed_bytes=sum(a != b for a,b in zip(raw,image)), CPU=cpu,
                  native_source_ingress_CPU=ingress, Prince105_disjoint=True,
                  limitations=['The private menu alternates DK/Jr only while focused. Returning to the slot defaults to DK.',
                               'The menu preview deliberately reuses the six-part DK family art and palette. Authentic Jr gameplay CHR stays exact.',
                               'Physical Mesen menu, cold controls, cadence and 1-1 remain to be qualified.'],
                  bindings={str(p):sha(p.read_bytes()) for p in [Path(__file__),Path(I.__file__),Path(UI.__file__),
                     I.ROM,I.UISTUDY,GRANT,R/'src/character_select.s',R/'src/full_roster_menu.s',
                     R/'tools/reference/thomas_hot_render_1031_v3.s',R/'build/mini-two-fireballs-1103/source-funding.json',
                     O/'installed-ingress.json',I.BASE/'native-cookie-v90.bin']})
    assert sha(I.ROM.read_bytes()) == I.PIN
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','expected_memory_only_SHA256','changed_bytes']}),flush=True)


if __name__ == '__main__':
    main()
