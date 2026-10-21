"""Check AP's compiled scalar placement, inherited art datasets and U filter."""
from pathlib import Path
import hashlib, importlib.util, json, re

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-advanced-union-ap'
P = V / 'root49-easy-ryu-union-ai'
F = V / 'agent49-enemy-geometry-advanced-g'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = H / 'binary-review-ar.json';assert not output.exists()
    assert sha(H / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    assert sha(F / 'admission-c2.json') == '2229d65ff7680d79df107df2671cc43bf842cb7e9cf38578a4fb469f2ea851a8'
    build = json.loads((H / 'report.json').read_text())
    admission = json.loads((F / 'admission-c2.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    datasets = []
    for name in admission['generated_datasets']:
        before = (P / 'source' / name).read_bytes();after = (H / 'source' / name).read_bytes()
        assert before == after
        datasets.append(dict(path=name, bytes=len(after), sha256=hashlib.sha256(after).hexdigest(), exact_AI_bytes=True))
    assert len(datasets) == 7
    before = (P / 'source/src/roster_weapons.s').read_text()
    after = (H / 'source/src/roster_weapons.s').read_text()
    pattern = r'\.proc RosterDrawShots\n.*?\.endproc'
    old = re.search(pattern, before, re.S)[0];new = re.search(pattern, after, re.S)[0]
    assert old == new and 'cmp #32' in new
    spec = importlib.util.spec_from_file_location('advanced_ar_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rows = []
    for mapper in ['mmc3', 'mmc5']:
        im = m.Image(H / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        original = m.Image(F / 'candidate-c2' / ('smb-crossover-' + mapper + '.nes'))
        parent = m.Image(P / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        def raw(image, name, count):
            x = image.hook(name)['rom_offset'];return image.raw[x:x + count]
        scalars = []
        for side in ['Right', 'Left']:
            for axis in ['XLo', 'XHi', 'YLo', 'YHi']:
                name = 'BillFlare' + side + axis
                def data(image):
                    return raw(image, name + 'Prefix', 96) + raw(image, name + 'Tail', 144) if name == 'BillFlareLeftXLo' else raw(image, name, 240)
                a, b = data(original), data(im)
                assert len(a) == len(b) == 240 and a == b
                assert hashlib.sha256(b).hexdigest() == admission['mappers'][mapper]['source_scalars'][name]['sha256']
                scalars.append(dict(name=name, bytes=240, sha256=hashlib.sha256(b).hexdigest(), exact_frozen_C2=True))
        for name in ['GrowthRadiusLo', 'GrowthRadiusHi']:
            assert raw(parent, name, 36) == raw(im, name, 36)
        assert im.ram == parent.ram and im.raw[:16] == parent.raw[:16] and im.raw[524304:] == parent.raw[524304:]
        oldcold = next(x for x in parent.segs.values() if x['name'] == 'LEGACY_COLD')
        newcold = next(x for x in im.segs.values() if x['name'] == 'LEGACY_COLD')
        end = oldcold['ooffs'] + oldcold['size'];newend = newcold['ooffs'] + newcold['size']
        assert newcold['ooffs'] == oldcold['ooffs'] and newend - end == 953 and set(parent.raw[end:newend]) == {255}
        rows.append(dict(mapper=mapper, ROM_sha256=sha(im.path), inherited_AI_RAM_header_CHR_size_exact=True,
                         source_orbit_scalar_bytes=1920, scalars=scalars, growth_72_scalar_bytes_equal_AI=True,
                         new_cold_953_bytes_replace_old_FF_tail=True,
                         entry_banks={name: im.hook(name)['physical_bank'] for name in ['RemainingWeapons', 'AvBillInput', 'BillAdvancedFlareStep', 'BillAdvancedFlarePublish', 'BillLaserSpacingParameters', 'BillFlareLoadLeft']}))
    report = dict(status='PASS_AP_COMPILED_ORBIT_SCALARS_INHERITED_ART_AND_SINGLE_RENDERER_SOURCE',
                  script_sha256=sha(__file__), build_sha256=sha(H / 'report.json'), datasets=datasets,
                  RosterDrawShots_AI_source_exact=True, mapper_rows=rows,
                  scope='Compiled1920 scalar bytes equal frozen high-precision-audited C2; inherited seven AI datasets preserve merged Link/Bill artwork. Native execution and source geometry are separate AQ evidence.',
                  route_proof=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(output), flush=True)


if __name__ == '__main__':
    main()
