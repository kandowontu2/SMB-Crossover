"""Close the current readers of one historically reserved SMB3Plus CHR page."""

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

import audit_getsu_frontend_1110 as Front
from check_tmnt_render_oa import address, location
from inventory_playable_menu_1101_v3 import menu_name


R, ROM, PIN = Front.R, Front.ROM, Front.PIN
PAGE = 990
CHR = 1048592
SOURCE = R / 'build/bt-ready-menu-1031-v2/joint'
AUTHORITY = R / 'build/mini-mario-owner-1103-v15/carrier-audit-v16.json'
WRITERS = R / 'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json'
ASSET = R / 'build/getsu-fuma-art-1110/proof.json'
DK = R / 'docs/qa/allocations/dkjr-private-resources-1102-v20.json'
MINI = R / 'docs/qa/allocations/mini-mario-private-resources-1103-v24.json'
SHA = lambda content: hashlib.sha256(content).hexdigest()


def load_json(path):
    return json.loads(path.read_text())


def span(raw, start, size):
    return dict(file_offset=start, bytes=size, SHA256=SHA(raw[start:start + size]))


def bundle():
    b = Front.scoped_load(Front.AUTHORITY)
    Front.merge(b, Front.scoped_load(Front.FAMILY), 'family')
    current = Front.scoped_load(ROM)
    Front.merge(b, current, 'current')
    b['raw'] = current['raw']
    assert SHA(b['raw']) == PIN
    return b


def verify_linked_source(b):
    raw, old = b['raw'], (SOURCE / 'candidate.nes').read_bytes()
    exact = {}
    # Original configured source still describes these actual instructions.
    for name, size in (('M3Graphics', 187), ('M3SetFrame', 147), ('MbPaletteAndBody', 74),
                       ('M3GrowFrames', 12), ('M3Form0ChrLo', 81), ('M3ChrLoTableLo', 28),
                       ('M3PublishBody', 26), ('X5PublishChr', 320)):
        at = location(b, name)
        assert raw[at:at + size] == old[at:at + size], name
        exact[name] = span(raw, at, size)
    tables = location(b, 'M3ChrLoTableLo')
    assert raw[tables:tables + 14] == bytes([0xee] * 7 + [0xcd] * 7)
    assert (SOURCE / 'src/smb3_mario_pickups.s').read_text().count('Grow:lda #47\n sta M3Growth') == 1
    assert (SOURCE / 'src/smb3_mario_dispatch.s').read_text().count('lda #47 ; Original PRG0 DA4E shrink;') == 1
    assert 'dec M3Growth\nPalette:jsr MbPaletteAndBody' in (SOURCE / 'src/smb3_mario_render.s').read_text()
    # Single absolute consumer of the C-window helper in the actual image.
    pattern = bytes.fromhex('2083cf')
    assert raw[16:CHR].count(pattern) == 1 and raw.find(pattern, 16, CHR) == Front.off(90, 0xa1d1)
    # Two source-declared retired low tables are possible resident staging.
    # The C aliases have no absolute jump or JSR in current PRG. This does
    # not grant the corresponding A-window aliases or menu ingress bytes.
    staging = {}
    for name in ('M3Form2ChrLo', 'M3Form3ChrLo'):
        at, pc = location(b, name), address(b, name)
        assert raw[at:at + 81] == bytes([0xea]) * 81
        assert name + ':\n .res 81,$ea' in (SOURCE / 'src/smb3_mario_art.inc').read_text()
        assert all(bytes([op, pc & 255, pc >> 8]) not in raw[16:CHR] for op in (0x20, 0x4c))
        staging[name] = dict(CPU_C=pc, CPU_A=pc - 0x2000, **span(raw, at, 81))
    return exact, staging


def verify_current_ledger(b):
    raw = b['raw']
    inherited = load_json(AUTHORITY)
    historical = load_json(WRITERS)
    assert inherited['passed'] and historical['passed']
    scopes = inherited['exact_finite_domains']
    assert [owner for owner, pages in scopes.items() if PAGE in pages] == [
        'Historical SMB3Plus retained conservative emission']
    dk, mini = load_json(DK), load_json(MINI)
    reservations = dk['code_pages'] + dk['art_and_helpers'] + mini['code_pages'] + [
        mini['immutable_page'], mini['art_page']]
    assert PAGE not in reservations
    for p in inherited['current_table_bindings']:
        assert span(raw, p['offset'], p['bytes'])['SHA256'] == p['SHA256'], p
    for p in inherited['inherited_private_writer_chunks_exact']:
        assert any(span(raw, CHR + n * 1024, 1024)['SHA256'] == p['SHA256'] for n in p['pages']), p
    for s in historical['native_spans']:
        expected = ('ad0260d006ad0a73c902603860eaeaea' if s['name'] == 'MaaLagChrGuard' else s['hex'])
        assert raw[s['offset']:s['offset'] + s['size']].hex() == expected, s['name']

    moves, exact = {}, 0
    for row in historical['unchanged_inherited_writers']:
        if Path(row['file']).suffix != '.nes':
            continue
        at = row['file_offset']
        before = bytes.fromhex(row['old_bytes'])
        now = raw[at:at + len(before)]
        if before == now:
            exact += 1
        else:
            moves[at] = (row['segment'], before.hex(), now.hex())
    assert exact == 794 and len(moves) == 22
    assert set(moves) == {17172, 1036458, 1036475, 1036510, 314270, 216014, 216142, 216148, 216151,
                          216157, 216160, 216166, 216169, 216175, 216181, 217232, 217802, 217831,
                          1953144, 1953403, 1953411, 1953416}
    current_sources = {}
    # The current parser patches reissue the bounded native block store and
    # retain provenance in the existing cell arrays below $68d4.
    parser = R / 'build/native-parser-paired-shadow-1110/proof.json'
    camera = R / 'build/helper-camera-admission-1110/proof.json'
    for path, changes in ((parser, (17172, 1036458, 1036475, 1036510)), (camera, (217802, 217831))):
        proof = load_json(path)
        assert proof['passed']
        for at in changes:
            row = next(p for p in proof['patches']
                       if p['file_offset'] <= at < p['file_offset'] + len(bytes.fromhex(p['new_hex'])))
            off, replacement = row['file_offset'], bytes.fromhex(row['new_hex'])
            assert raw[off:off + len(replacement)] == replacement
        current_sources[path.parent.name] = SHA(path.read_bytes())
    # The current XG history store moved two bytes, with its same $e3/$e4
    # ring pointer and $7400..$7bff bounds. No indirect CHR register target.
    assert raw[314269:314292].hex() == 'c6e28a91e3e6e3d00ce6e4a5e4c97cd004a97485e48a60'
    # Live helper control no longer writes to the old indexed origin. Its
    # relocated init/camera state is in the existing bounded $7382..$73dd
    # block, before $73e0 CHR modes. The other rewrites hit native actor RAM.
    assert address(b, 'HpRamStart') == 0x7382 and address(b, 'HpRamEnd') <= 0x73e0
    assert raw[217228:217233].hex() == 'a9008dc173'
    assert all((at - CHR) // 1024 == 883 for at, row in moves.items() if row[0] == 'ARTHUR_CACHE_EXEC')
    # The actual DK replacement and all Mini pages already have reservations.
    reviewed = R / 'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
    existing = reviewed.read_bytes()
    assert SHA(existing) == inherited['current_ROM_SHA256']
    assert all(raw[CHR + n * 1024:CHR + (n + 1) * 1024] == existing[CHR + n * 1024:CHR + (n + 1) * 1024]
               for n in dk['code_pages'] + dk['art_and_helpers'])
    return dict(direct_exact=exact, changed=moves, source_receipts=current_sources,
                exact_selector_tables=len(inherited['current_table_bindings']),
                exact_private_writer_chunks=len(inherited['inherited_private_writer_chunks_exact']),
                reservations=reservations)


def exercise_smb3(b):
    seed = Front.N.fresh(b)
    put, run = Front.N.put, Front.F.invoke
    put(seed, SelectedCharacter=17, OperMode=1, M3Ready=179, M3Poof=0, VRAM_Buffer1_Offset=0,
        MmDeathFlag=0, MmDeathPit=0, GuestInvulTicks=0)
    seed[0x5f4f] = 179  # Source M3Ensure's established owner marker.
    main, growth, deaths = Counter(), Counter(), Counter()

    def one(variant, form, frame, face, grow=0, death=0, pit=0, flip=0):
        # A single fixture bus may be reused because each selector overwrites
        # both page bytes and current pose before the source publication.
        put(seed, M3Variant=variant, M3Form=form, M3Growth=grow, MmDeathFlag=death, MmDeathPit=pit,
            PlayerFacingDir=face, VRAM_Buffer1_Offset=0)
        seed[0x5c1e], seed[0x5c32], seed[0x5c1f] = frame, flip, flip << 6
        seed.writes.clear()
        run(seed, 'M3Graphics')
        if pit:
            assert seed[address(b, 'ObjectMetasprite')] == 0
            return 'hidden'
        run(seed, 'M3PublishBody')
        run(seed, 'X5PublishChr')
        actual = seed.chr_latches[0]
        assert actual != PAGE and actual == seed[0x6b08] + (seed[0x5c87] << 8), (variant, form, frame, face, grow)
        return actual

    for case in itertools.product(range(4), range(7), range(256), (1, 2)):
        main[one(*case)] += 1
    for variant, form, grow, face in itertools.product(range(4), range(7), range(1, 48), (1, 2)):
        growth[one(variant, form, 14, face, grow=grow)] += 1
    for variant, form, face, pit in itertools.product(range(4), range(7), (1, 2), (0, 1)):
        deaths[one(variant, form, 14, face, death=1, pit=pit)] += 1
    for variant, form, frame, face, flip in itertools.product(range(4), range(7), range(26, 30), (1, 2), range(1, 4)):
        main[one(variant, form, frame, face, flip=flip)] += 1
    return dict(normal_and_flip=sum(main.values()), growth=sum(growth.values()), deaths=sum(deaths.values()),
                published=sorted((set(main) | set(growth) | set(deaths)) - {'hidden'}),
                historical_atlas_published=sorted(p for p in set(main) | set(growth) if 969 <= p < 1019))


def exercise_current_menu(b):
    put, run = Front.N.put, Front.F.invoke
    profiles, pages = [], set()
    for slot in range(32):
        m = Front.N.fresh(b)
        put(m, CrossoverMenuIndex=slot, CmActive=0)
        m[0x5ffe] = 0
        run(m, 'MenuResolveCharacter')
        run(m, 'QueueSelection')
        seen = set()
        for _ in range(32):
            name, cells = menu_name(m)
            rawid = m[0x6002]
            sig = (rawid, tuple(cells), bytes(m[0x5fe0:0x5fff]), m[0x730a])
            if sig in seen:
                break
            seen.add(sig)
            profiles.append((slot, rawid, name))
            view = Front.N.fork(m)
            put(view, VRAM_Buffer1_Offset=0)
            run(view, 'DrawSelectionPreview')
            run(view, 'X5PublishChr')
            pages.update(view.chr_latches)
            assert PAGE not in view.chr_latches, profiles[-1]
            put(m, VRAM_Buffer1_Offset=0, CrossoverMenuButtons=0, SavedJoypad1Bits=32, SavedJoypad2Bits=0)
            run(m, 'CrossoverMenuInput')
        else:
            raise AssertionError(('menu cycle cap', slot))
    assert (len(profiles), len(set(profiles))) == (100, 94)
    assert not any(row[1] == 42 for row in profiles)
    return dict(machine_states=len(profiles), named=len(set(profiles)), published=sorted(pages))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(R / 'build')
    b = bundle()
    raw = b['raw']
    exact, staging = verify_linked_source(b)
    ledger = verify_current_ledger(b)
    art = load_json(ASSET)
    assert art['passed'] and art['bytes']['chr_page'] == 1024
    assert SHA((ASSET.parent / 'atlas.chr').read_bytes()) == art['outputs']['atlas.chr']
    smb3 = exercise_smb3(b)
    menu = exercise_current_menu(b)
    result = dict(passed=True, current_SHA256=PIN, resource_granted=False, ROM_written=False,
                  private_source_only=True, page=PAGE, physical=span(raw, CHR + 1024 * PAGE, 1024),
                  replacement_atlas_SHA256=art['outputs']['atlas.chr'],
                  source_selector=exact, legacy_writer_rebind=ledger, actual_SMB3Plus=smb3,
                  actual_current_menu=menu, possible_staging_preimages=staging,
                  limits=['Current finite source readers and settled publications. Instruction-cut publication and new preview ingress need a separate proof.',
                          'Historical broad atlas extent 969..1018 remains reserved except for any future exact root grant.',
                          'No public raw42, no reuse of DK menu/art and no atlas installation.'],
                  bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in (Path(__file__), ROM,
                            AUTHORITY, WRITERS, ASSET, DK, MINI, SOURCE / 'candidate.nes',
                            *(SOURCE / 'src' / name for name in ('smb3_mario_render.s', 'smb3_mario_art.inc',
                                                                 'smb3_mario_dispatch.s', 'smb3_mario_pickups.s')))})
    args.output.mkdir(exist_ok=True)
    (args.output / 'atlas-page.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('passed', 'physical', 'actual_SMB3Plus', 'actual_current_menu')}))


if __name__ == '__main__':
    main()
