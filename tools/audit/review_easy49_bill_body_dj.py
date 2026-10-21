"""Verify the frozen Bill correctness packet and its exact private DG runtime."""
from pathlib import Path
import hashlib
import importlib.util
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
F = V / 'agent49-bill-source-body-f'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root49-bill-body-review-dj.json'
    assert not output.exists()
    freeze_path = F / 'freeze-m.json'
    assert sha(freeze_path) == '36910e7b6568bf15c31d59d53326a03ac0ce2007a4f7aae9f437d950e31ccc70'
    freeze = json.loads(freeze_path.read_text())
    assert freeze['positive_cases'] == 2 * (2784 + 2112 + 88 + 5) == 9978
    pins = []
    def verify(value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                p = Path(value['path'])
                if not p.is_absolute():
                    p = F / p
                assert sha(p) == value['sha256'], p
                if 'bytes' in value:
                    assert p.stat().st_size == value['bytes'], p
                pins.append(dict(path=p.relative_to(R).as_posix(), sha256=sha(p)))
            for x in value.values():
                verify(x)
        elif isinstance(value, list):
            for x in value:
                verify(x)
    verify(freeze)
    receipts = json.loads((F / freeze['receipt_catalog']['path']).read_text())
    assert len(receipts) == 211
    for name, row in receipts.items():
        p = F / name
        assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes'], p
    source_freeze = json.loads((F / freeze['source_freeze']['path']).read_text())
    source = Path(source_freeze['source'])
    catalog = json.loads((F / freeze['source_catalog']['path']).read_text())
    assert len(catalog) == 441 and all(sha(source / n) == h for n, h in catalog.items())
    for name, digest in freeze['source_receipts'].items():
        assert sha(F / name) == digest
    dg_path = V / 'root49-bill-body-union-dg/report.json'
    assert sha(dg_path) == '3252ea899aa312e7cf8efefeabed360401d32589f468ddb6997dacc7dcb3ad43'
    dg = json.loads(dg_path.read_text())
    assert all(sha(dg_path.parent / 'source' / n) == h for n, h in dg['source_hashes'].items())
    spec = importlib.util.spec_from_file_location('body_dj_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    image_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(image_module)
    rows = []
    for mapper, data in freeze['maps'].items():
        native = image_module.Image(Path(data['ROM']['path']))
        parent = image_module.Image(V / 'root49-easy-combined-bq/source/build' / ('smb-crossover-' + mapper + '.nes'))
        assert all(native.ram[n] == address for n, address in parent.ram.items())
        assert {n: a for n, a in native.ram.items() if n not in parent.ram} == dict(BillSourceBodyForm=0x7fe5, BillSourceFlagSeen=0x7fe6)
        assert native.raw[:16] == parent.raw[:16] and native.raw[524304:] == parent.raw[524304:]
        audio_count = 0
        for name, audio in data['audio_segments_exact'].items():
            offset, size = audio['offset'], audio['size']
            block = native.raw[offset:offset + size]
            assert block == parent.raw[offset:offset + size]
            assert hashlib.sha256(block).hexdigest() == audio['sha256']
            audio_count += 1
        merged_rom = dg_path.parent / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        assert sha(merged_rom) == sha(Path(data['ROM']['path']))
        rows.append(dict(mapper=mapper, rom_sha256=sha(merged_rom), old_RAM_exact=len(parent.ram),
                         appended_RAM=data['appended_RAM'], audio_segments_exact=audio_count,
                         DG_runtime_exact=True, header_CHR_exact=True))
    report = dict(status='PASS_FROZEN_BODY_F_CORRECTNESS_CONTROL_AND_DG_RUNTIME_TRANSFER',
        script_sha256=sha(__file__), freeze_sha256=sha(freeze_path), DG_report_sha256=sha(dg_path),
        pinned_references=pins, receipt_files=211, source_files=441,
        positive_native_cases=9978, actor_cases_are_body_subset=True, mappers=rows,
        admission='Correctness control/private DG only. No main install. Exact-threshold optimization descendant remains pending because the measured ~720 added active Bill cycles is material for walking lag.',
        limits='Source integer-enemy-proxy actor predicates, source fractional rectangles, head/tile sampling, native terrain resolution, platform and bitmap firebar paths remain separate. The two original enemy contacts still overlap corrected native-proxy boxes; their full source-enemy verdict is unclassified.',
        retained_negatives='All211 frozen receipt files include prior harness/placement/facing/PLY/cache negatives; only frozen final reproduction results constitute positive admission.',
        main_changed=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(output))


if __name__ == '__main__':
    main()
