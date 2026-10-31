"""Actual CF-ready menu/Start source consumer pairs, no native admission claim."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import bowser_current64_menu_controls_v1 as M
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address, location

T, H, C = M.T, M.H, M.C
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def snapshot(m):
    b = m.bundle
    return dict(queue=M.queue(m).hex(), OAM=bytes(m[512:768]).hex(),
                softwareCHR=bytes(m[address(b, 'CurrentCHRBank'):address(b, 'CurrentCHRBank') + 12]).hex(),
                modes=bytes(m[address(b, 'X5ChrMode'):address(b, 'X5ChrMode') + 12]).hex())


def menu(old, new):
    rows = []
    cf = []
    ready = [0, 0]
    for slot, count in enumerate(M.COUNTS):
        pair = []
        for b in [old, new]:
            m = C.fresh(b, 0)
            H.put(m, CrossoverMenuIndex=slot, FfVariant=0, FmAlts=0)
            C.invoke(m, 'MenuResolveCharacter')
            C.invoke(m, 'QueueSelection')
            pair.append(m)
        for variant in range(count):
            if variant:
                for m in pair:
                    H.put(m, CrossoverMenuButtons=0, SavedJoypad1Bits=32, SavedJoypad2Bits=0, VRAM_Buffer1_Offset=0)
                    C.invoke(m, 'CrossoverMenuInput')
            got = []
            for index, m in enumerate(pair):
                call = C.invoke(m, 'FmPending')
                state = dict(selected=H.get(m, 'SelectedCharacter'), nameindex=call['AXYP_SP'][0],
                             pending=call['AXYP_SP'][3] & 1, **snapshot(m))
                ready[index] += not state['pending']
                got.append(state)
            if slot != 30:
                assert got[0] == got[1], ('Foreign menu/name/OAM/CHR byte pair', slot, variant, got)
            else:
                assert got[0]['pending'] == 1 and got[1]['pending'] == 0
                assert got[0]['selected'] == 0 and got[1]['selected'] == 31
                assert got[0]['nameindex'] == got[1]['nameindex'] == 26 + variant
                assert H.get(pair[1], 'FmGroups') & 24 == variant << 3
                old_oam = bytes.fromhex(got[0]['OAM'])
                new_oam = bytes.fromhex(got[1]['OAM'])
                assert new_oam == old_oam, ('Authentic existing CF preview changed', variant)
                parts = [list(new_oam[i:i + 4]) for i in range(0, 256, 4) if new_oam[i] < 240]
                assert len(parts) == 5 and {r[2] & 3 for r in parts} == {0, 1}
                # Ready native preparation legitimately fills unused sprite
                # windows4..7. Prove the genuine source sprite consumers and
                # all four title BG windows instead of treating unused state
                # bytes as visible graphics. The failedv1 arrays stay bound.
                old_chr, new_chr = [bytes.fromhex(got[i]['softwareCHR']) for i in range(2)]
                old_modes, new_modes = [bytes.fromhex(got[i]['modes']) for i in range(2)]
                used = {(r[1] & 1) * 4 + ((r[1] & 254) * 16) // 1024 for r in parts}
                assert used <= set(range(4))
                assert old_chr[:4] == new_chr[:4] == bytes([188, 189, 190, 191])
                assert old_modes[:4] == new_modes[:4] == bytes([130]) * 4
                assert old_chr[8:] == new_chr[8:] and old_modes[8:] == new_modes[8:]
                patterns = []
                for b, m in zip([old, new], pair):
                    C.invoke(m, 'X5PublishChr')
                    current = []
                    for y, tile, attr, x in parts:
                        at = (tile & 1) * 4096 + (tile & 254) * 16
                        window = at // 1024
                        page = m.chr_latches[window]
                        start = 16 + 128 * 8192 + page * 1024 + at % 1024
                        current.append(list(b['raw'][start:start + 32]))
                    patterns.append(current)
                assert patterns[0] == patterns[1] and all(any(row) for row in patterns[1])
                cf.append(dict(variant=variant, selected=31, name_index=26 + variant,
                               exact_existing_preview_OAM=True, visible_parts=parts,
                               native_groups=H.get(pair[1], 'FmGroups'), queue=got[1]['queue'],
                               actual_source_sprite_windows=sorted(used), final_hardware_patterns_exact=True,
                               title_BG_windows8_11_exact=True, old_new_softwareCHR=[list(old_chr), list(new_chr)]))
            rows.append(dict(slot=slot, variant=variant, selected=got[1]['selected'],
                             name_index=got[1]['nameindex'], pending=got[1]['pending'],
                             foreign_pair_exact=slot != 30))
    assert len(rows) == 83 and ready == [70, 74], ready
    # Source hints really alias one20B byte string. Every old label consumer
    # resolves through actual reassembly, rather than a pointer byte patch.
    names = ['DwHint', 'Z2Hint', 'TnHint', 'CdHint', 'Cv3Hint', 'M3Hint', 'ProtoHint']
    hint_addresses = [address(new, 'QueueVariantHint::' + n) for n in names]
    assert len(set(hint_addresses)) == 1
    name_lo = location(new, 'FmNames')
    raw_names = [list(new['raw'][name_lo + i * 16:name_lo + (i + 1) * 16]) for i in range(26, 30)]
    for oldrow, newrow in zip([old['raw'][location(old, 'FmNames') + i * 16:location(old, 'FmNames') + (i + 1) * 16] for i in range(26, 30)], raw_names):
        assert bytes(newrow) == bytes(oldrow).replace(bytes([63]), bytes([36]))
    return dict(actual_all83_source_menus=rows, previous70_ready_preserved=True,
                source_menu_ready_counts=ready, four_CF_preview_cases=cf,
                lossless_hint_alias_addresses=hint_addresses, CF_name_rows=raw_names)


def start(new):
    seed = T.make(new)
    cases = 0
    for slot, p, bits in itertools.product(range(32), range(64), [0, 24, 32, 128, 255]):
        m = T.fork(seed)
        H.put(m, FmAlts=bits, FmGroups=bits)
        flags = T.flags(p)
        c, low = T.call(m, 'FmStartFlags', x=slot, a=0x55, y=0x63, p=flags)
        assert (c.a, c.x, c.y, c.p, c.sp) == (0, slot, 0x63, (flags & 0x7d) | 2, 224)
        assert H.get(m, 'FmAlts') == bits & {9: 32, 26: 8, 31: 128}.get(slot, 0)
        assert H.get(m, 'FmGroups') == bits & {23: 32, 30: 24}.get(slot, 0)
        cases += 1
    return dict(actual_Start_flag_cases=cases, CF_class_bits18_preserved_only_slot30=True,
                prior_Bowser_Quick_Arthur_BT_identity_masks_exact=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-joint', type=Path, required=True)
    ap.add_argument('--cart-root', type=Path, required=True)
    ap.add_argument('--output-root', type=Path, required=True)
    args = ap.parse_args()
    out = args.output_root.resolve()
    assert not out.exists()
    out.mkdir(parents=True)
    q = dict(passed=False, source_CPU=True, native=False, admitted=False, checks={},
             retained_v1_fixture_negative=dict(path=str(R / 'build/contra-force-menu-admission-controls-1031-v1/controls.json'),
                 sha256=sha(R / 'build/contra-force-menu-admission-controls-1031-v1/controls.json'),
                 correction='Ready native preparation writes otherwise-unused sprite slots4..7; actual five CF preview parts use only0..3. V2 checks all title BG8..11 and actual published physical patterns for every part, preserving exact OAM/palettes/source colors. No ROM change.'))
    try:
        stage = json.loads((args.cart_root / 'source-stage.json').read_text())
        for path, digest in stage['bindings'].items():
            assert sha(path) == digest, path
        old = qualified(args.parent_joint / 'candidate.nes')
        new = qualified(args.cart_root / 'joint/candidate.nes')
        q['checks']['menus'] = menu(old, new)
        q['checks']['Start'] = start(new)
        q['passed'] = True
    except Exception as error:
        q.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        q['bindings'] = {str(p.resolve()): sha(p) for p in [Path(__file__), Path(M.__file__),
            args.parent_joint / 'candidate.nes', args.parent_joint / 'candidate.dbg',
            args.cart_root / 'source-stage.json', args.cart_root / 'joint/candidate.nes', args.cart_root / 'joint/candidate.dbg',
            R / 'build/contra-force-menu-admission-controls-1031-v1/controls.json']}
        target = out / 'controls.json'
        target.write_text(json.dumps(q, indent=2) + '\n')
        print(json.dumps(dict(path=str(target), sha256=sha(target), passed=q['passed'], error=q.get('error'))), flush=True)


if __name__ == '__main__':
    main()
