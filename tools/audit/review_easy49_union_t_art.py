"""Decode actual combined CHR/metasprites and compare frozen source-art closures."""
from pathlib import Path
import hashlib, importlib.util, json
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-union-t'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dependency = V / 'agent49-bill-growth-e/review_art.py'
    spec = importlib.util.spec_from_file_location('union_t_art_reader', dependency)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    report = dict(status='REVIEWING_COMPILED_UNION_T_ART', script_sha256=sha(__file__),
                  reader_sha256=sha(dependency), build_review_sha256=sha(H / 'report.json'), rows=[], errors=[])
    for mapper in ['mmc3', 'mmc5']:
        name = 'smb-crossover-' + mapper + '.nes'
        new = m.m.Image(H / 'source/build' / name)
        old = m.m.Image(V / 'root49-easy-cold-bank-n/source/build' / name)
        link = m.m.Image(V / 'agent-lsr-easy-link-rect-animation-k/frozen-l' / name)
        growth = m.m.Image(V / 'agent49-bill-growth-e/candidate' / name)
        counts = dict(old_body_entries=0, frozen_Link_L_entries=0, frozen_Bill_Lance_growth_entries=0,
                      frozen_growth_weapon_records=0)

        def compare(a, b, role, index, side, label):
            ba = m.data(a, 'Rg' + role + 'Banks', 144)[index]
            bb = m.data(b, 'Rg' + role + 'Banks', 144)[index]
            ap, an = m.composite(a, (role, index, side), m.bank(a, ba))
            bp, bn = m.composite(b, (role, index, side), m.bank(b, bb))
            if ap != bp or an != bn:
                report['errors'].append([mapper, label, role, index, side])

        for role in ['BILL', 'LANCE', 'LINK', 'SIMON']:
            for index in range(144):
                for side in ['Left', 'Right']:
                    if role != 'LINK' or index % 48 not in [17, 18, 19]:
                        compare(old, new, role, index, side, 'original_body')
                        counts['old_body_entries'] += 1
                    if role == 'LINK':
                        compare(link, new, role, index, side, 'frozen_Link_L')
                        counts['frozen_Link_L_entries'] += 1
                    if role in ['BILL', 'LANCE']:
                        compare(growth, new, role, index, side, 'frozen_growth')
                        counts['frozen_Bill_Lance_growth_entries'] += 1
        for weapon in ['BULLET1', 'BULLET2', 'SPREAD5', 'SPREAD6', 'SPREAD7', 'SPREAD8', 'IMPACT']:
            for role in ['BILL', 'LANCE']:
                for side in ['Left', 'Right']:
                    # Lance shares Bill's weapon records and reserves their
                    # exact tile prefix in his own active body banks.
                    symbol = 'RgBILL' + weapon + side
                    ga = m.data(growth, 'Rg' + role + 'Banks', 144)[0]
                    ta = m.data(new, 'Rg' + role + 'Banks', 144)[0]
                    assert m.composite(growth, symbol, m.bank(growth, ga)) == m.composite(new, symbol, m.bank(new, ta)), (mapper, symbol)
                    counts['frozen_growth_weapon_records'] += 1
        allowed = set(range(0x1d, 0x3c)) | set(range(0xd1, 0xd5)) | set(range(0x74, 0x78)) | set(range(0x7a, 0x80))
        changed = [i for i in range(256) if m.bank(old, i) != m.bank(new, i)]
        unexpected = sorted(set(changed) - allowed)
        if unexpected:
            report['errors'].append([mapper, 'unrelated_logical_CHR', unexpected])
        report['rows'].append(dict(mapper=mapper, ROM_sha256=sha(new.path), counts=counts,
                                   changed_logical_banks=changed, unrelated_changes=unexpected))
    assert sha(H / 'source/chr/characters/ordinary-body-layout.json') == sha(V / 'root49-easy-cold-bank-n/source/chr/characters/ordinary-body-layout.json')
    report['status'] = 'PASS_COMBINED_COMPILED_SOURCE_ART_AND_OLD_BODY_PIXELS' if not report['errors'] else 'NEGATIVE_COMBINED_ART'
    report['qualification'] = 'Decoded compiled bitmap/part-order comparison only; actual native DMA tests and ordinary videos remain separate.'
    path = H / 'compiled-art-review.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(path), json.dumps(report['errors']))
    assert not report['errors']


if __name__ == '__main__':
    main()
