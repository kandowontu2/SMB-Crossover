"""Verify the final H admission packet and BQ's unchanged native oracles."""
from pathlib import Path
import hashlib, json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
F = V / 'agent49-bill-advanced-parity-h'
B = V / 'root49-easy-combined-bq'
O = V / 'root49-bill-freeze-review-cb'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(F / 'freeze-m.json') == '74da58b596109108566d706f9083a288f0f360f12c1ea99c5b7ee4e6c15b2252'
    assert sha(F / 'reproduction-m.json') == '33badcc9e0b36a2dd3147b58adc8192ace82133660021ba6300e7287bcb75aa6'
    frozen = json.loads((F / 'freeze-m.json').read_text())
    assert frozen['status'] == 'FROZEN_PASS_BILL_ADVANCED_H_M'
    assert frozen['native_component_cases'] == 4200 and frozen['native_component_cases_per_mapper'] == 2100
    assert frozen['source_counts'] == dict(parent=428, final=439, changed_or_new=23, removed=0)
    refs = {}
    def inspect(value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                path = Path(value['path'])
                assert sha(path) == value['sha256'], path
                if 'bytes' in value:
                    assert path.stat().st_size == value['bytes'], path
                refs[str(path.relative_to(R))] = value['sha256']
            for item in value.values():
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
    inspect(frozen)
    reproduction = json.loads((F / 'reproduction-m.json').read_text())
    inspect(reproduction)
    receipts = json.loads(Path(frozen['receipt_catalog']['path']).read_text())
    for name, values in receipts.items():
        path = F / name
        assert sha(path) == values['sha256'] and path.stat().st_size == values['bytes'], path
    source = json.loads(Path(frozen['final_catalog']['path']).read_text())
    assert len(source) == 439
    assert all(sha(Path(frozen['merged_AP_M_source']) / n) == h for n, h in source.items())
    assert frozen['additional_aliases_only'] == {mp: {'BillDrawTurn': 32639, 'BillDrawOtherCursor': 32640} for mp in ['mmc3', 'mmc5']}
    for mp, files in frozen['built_files'].items():
        assert all(sha(Path(frozen['merged_AP_M_source']) / 'build' / ('smb-crossover-' + mp + '.' + ext)) == h for ext, h in files.items())
    envelope = json.loads(Path(frozen['lifetime_source_envelope']['path']).read_text())
    assert envelope['max_MAP_NES_width'] == 6400
    assert envelope['castle_exception']['conservative_viewport_right_NES'] == 5356
    assert envelope['coverage_proof']['conservative_expiry_update'] == 3666
    assert envelope['coverage_proof']['runtime_age_kill'] is False
    for item in frozen['all_final_reports']:
        result = json.loads(Path(item['path']).read_text())
        assert result['status'].startswith('PASS'), item['path']
    bw = V / 'root49-bq-bill-rebind-bw'
    # The only changed oracle expression is the birth review's host output root.
    ca = V / 'root49-bq-bill-rebind-ca'
    adapter = json.loads((ca / 'report.json').read_text())
    changed = []
    for name, values in adapter['copied_inputs'].items():
        assert sha(F / name) == values['original']
        assert sha(ca / name) == values['actual']
        if values['original'] != values['actual']:
            changed.append(name)
            expected = (F / name).read_text().replace("H=Path('build/verification/agent49-bill-advanced-parity-h')", 'H=Path(__file__).resolve().parent')
            assert (ca / name).read_text() == expected
    assert changed == ['review_birth.py']
    assert sha(bw / 'report.json') == adapter['previous_report_sha256']
    O.mkdir(exist_ok=False)
    report = dict(status='PASS_FROZEN_BILL_H_M_ADMISSION_PACKET', script_sha256=sha(__file__),
                  final_freeze_sha256=sha(F / 'freeze-m.json'), reproduction_sha256=sha(F / 'reproduction-m.json'),
                  receipt_files_checked=len(receipts), nested_references_checked=len(refs), final_source_files_checked=439,
                  all_final_reports_checked=len(frozen['all_final_reports']),
                  BQ_bindings_cores_oracles_unchanged_except_birth_host_root=True,
                  source_envelope=dict(max_width=6400, castle_conservative_right=5356, conservative_update=3666,
                                       source_angles=4096, arbitrary_age_kill=False),
                  qualifications=frozen['source_qualifications'], references=refs,
                  actual_combined_native_admission_still_pending=True,
                  accepted_release=False, goal_complete=False)
    (O / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(O / 'report.json'), 'receipts', len(receipts), flush=True)


if __name__ == '__main__':
    main()
