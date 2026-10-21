"""Finish L after preserving the flattened-label host guard negative."""
from pathlib import Path
import json
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_samus49_water_private import ROOT, K, PACKET, OWN, sha


def main():
    report_path = OWN / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['status'] == 'building-private-only'
    assert report['cases'] == [{'mapper': 'mmc3', 'exit': 0}]
    source = OWN / 'source'
    assert all(sha(source / n) == h for n, h in report['source407_hashes'].items())
    negative = OWN / 'layout-guard-negative-a.json'
    assert not negative.exists()
    negative.write_text(json.dumps(dict(status='HOST_LAYOUT_GUARD_NEGATIVE', report_before=report,
        reason='The first validator flattened scoped LBL names. Expected Samus local shifts and new Samus DirectionReady shadowed same-name labels in other procedures. It did not establish a global-PC/runtime failure.',
        original_builder_sha256=sha(ROOT / 'tools/audit/build_samus49_water_private.py'),
        first_mmc3_ROM_sha256=sha(source / 'build/smb-crossover-mmc3.nes'),
        no_native_execution=True), indent=2) + '\n')
    report.update(status='finishing-scoped-layout-check', layout_guard_negative_sha256=sha(negative),
                  completion_script_sha256=sha(Path(__file__)))
    report['cases'] = []
    contract = json.loads((PACKET / 'contract.json').read_text())
    sys.path.insert(0, str(ROOT / 'build/verification/agent49k-samus-water-up-direction-component-a'))
    from image import Image
    for mapper, number in [('mmc3', 4), ('mmc5', 5)]:
        if mapper == 'mmc5':
            assert not (OWN / 'build-mmc5.log').exists()
            with (OWN / 'build-mmc5.log').open('w', encoding='utf-8') as log:
                done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=source, stdout=log, stderr=subprocess.STDOUT)
            assert done.returncode == 0
        old = K / f'source/build/smb-crossover-{mapper}.nes'
        new = source / f'build/smb-crossover-{mapper}.nes'
        a, b = Image(old), Image(new)
        assert len(a.raw) == len(b.raw) == 786448
        delta = [i for i, (x, y) in enumerate(zip(a.raw, b.raw)) if x != y]
        assert delta and all(16 + 10 * 8192 <= i < 16 + 11 * 8192 for i in delta)
        def globals(im):
            return {s['name']: s['val'] for s in im.data['sym'] if s.get('scope') == 1 and 'val' in s and 'seg' in s}
        assert all(globals(b).get(n) == value for n, value in globals(a).items())
        layout = contract['before_layout'][str(number)]
        for n, address in layout['expected_scoped_labels'].items():
            assert b.sym(n, 'SamusMovement')['val'] == address, (mapper, n)
        assert b.sym('DirectionReady', 'SamusMovement')['val'] == layout['expected_new_DirectionReady']
        # Other procedures' same-name DirectionReady symbols retain their PCs.
        other_direction = [s for s in a.data['sym'] if s.get('name') == 'DirectionReady' and 'seg' in s]
        for s in other_direction:
            scope = a.scopes[s['scope']]['name']
            assert b.sym('DirectionReady', scope)['val'] == s['val']
        sa, sb = a.segs[a.sym('SamusMovement')['seg']], b.segs[b.sym('SamusMovement')['seg']]
        assert (sa['start'], sa['size'], sa['ooffs']) == (sb['start'], sb['size'], sb['ooffs'])
        def read(im, start, end):
            seg = im.segs[im.sym('SamusMovement')['seg']]
            offset = seg['ooffs'] + start - seg['start']
            return im.raw[offset:offset + end - start]
        assert read(a, layout['movement_start'], layout['old_query_start']) == read(b, layout['movement_start'], layout['old_query_start'])
        assert list(read(b, layout['expected_new_Direction'], layout['expected_new_DirectionReady'])) == layout['old_query_bytes']
        suffix = layout['expected_unchanged_suffix']
        assert read(a, suffix['start'], suffix['end_exclusive']) == read(b, suffix['start'], suffix['end_exclusive'])
        report['cases'].append(dict(mapper=mapper, exit=0, ROM_sha256=sha(new), DBG_sha256=sha(new.with_suffix('.dbg')),
            LBL_sha256=sha(new.with_suffix('.lbl')), changed_ROM_bytes=len(delta), changes_confined_to_SAMUS=True,
            scoped_global_symbols_exact=True, scoped_local_labels_match_contract=True,
            other_procedure_DirectionReady_labels_exact=True, moved23bytes_exact=True,
            prefix_and_suffix_exact=True, SAMUS_size=sb['size'], SAMUS_growth=0, SRAM_growth=0))
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert all(sha(source / n) == h for n, h in report['source407_hashes'].items())
    report.update(status='PASS-build-and-scoped-layout-only-not-accepted', source407_exact_after=True,
                  original_mmc3_not_rebuilt=True, goal_complete=False)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'source407_hashes'}), flush=True)


if __name__ == '__main__':
    main()
