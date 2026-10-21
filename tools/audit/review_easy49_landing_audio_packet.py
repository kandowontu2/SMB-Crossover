"""Review the frozen independent landing correction without widening its scope."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/agent49-sophia-land-audio-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = R / 'build/verification/root49-landing-audio-admission-a.json'
    assert not out.exists()
    frozen = D / 'freeze.json'
    catalog_path = D / 'receipt-catalog.json'
    assert sha(frozen) == '89b777ca536ea791d3af7091ba56c3039929f740c2fe9c43aad25b332811d05a'
    assert sha(catalog_path) == '5438bfb0cb9b8e70387b1b847e68e9781ab4cfdf7afff4eba7b844b2a7c94415'
    f, catalog = [json.loads(p.read_text()) for p in (frozen, catalog_path)]
    assert len(catalog) == f['retained_receipt_files'] == 304
    for name, item in catalog.items():
        p = D / name
        assert p.stat().st_size == item['bytes'] and sha(p) == item['sha256'], name
    checked = set()

    def walk(value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                p = Path(value['path'])
                if not p.is_absolute():
                    p = R / p
                assert p.is_file() and sha(p) == value['sha256'], str(p)
                checked.add(str(p))
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(f)
    assert not f['owned_live_handles'] and not f['main_installed']
    assert len(f['build_artifacts']) == 4 and sum(map(len, f['build_artifacts'].values())) == 16
    statuses = {name: item['status'] for name, item in f['reports'].items()}
    classified = {
        'source-c-landing-retrigger-defect.json': 'DEMONSTRATED_SOURCE_C_EXTRA_TIMER_HIGH_RETRIGGERS_BOTH_MAPPERS_AND_MODES',
        'scope-clarifications.json': 'ADDITIVE_SCOPE_CORRECTIONS_AND_LIMITS',
    }
    assert all(statuses[name] == status for name, status in classified.items())
    assert all(status.startswith('PASS') for name, status in statuses.items() if name not in classified), statuses
    report = dict(status='PASS_ROOT_SCOPED_LANDING_AUDIO_ADMISSION_REVIEW', script_sha256=sha(__file__),
        freeze_sha256=sha(frozen), receipt_catalog_sha256=sha(catalog_path), rehashed_receipt_files=304,
        frozen_reference_records_checked=len(checked), source_files=f['source_e']['source_files'],
        scope_counts=f['scope_counts'], cost=f['cost'], qualifications=f['qualifications'],
        final_report_statuses=statuses, retained_negative_and_scope_reports=classified,
        root_did_not_rerun_specialist_native_or_compiled_checks=True,
        runtime_scope='Only immutable root49-sophia-land-fix-a/source-e. A later optimized successor must retain literal audio or supply new evidence.',
        main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out), rehashed_files=304)))


if __name__ == '__main__':
    main()
