"""Append qualified route/audio progress; retain every earlier receipt."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'build/verification/root-current49-progress-d.json'
    assert not out.exists()
    prior = ROOT / 'build/verification/root-current49-progress-c.json'
    report = json.loads(prior.read_text())
    refs = {
        'SamusF_D_exact_late_Goomba_owner': 'build/verification/agent49f-samus-late-goomba-controller-e/actual-d-receipt.json',
        'SamusF_E_later_Paratroopa_negative': 'build/roster-through-2-2/root49f-samus-late-goomba-live-e-2-v0-mmc3/manifest.json',
        'RyuG_B_two_swings_and_fall_classification': 'build/verification/ryu49g-redkoopa-b-classification-a/report.json',
        'RyuG_C_mounted_cap_then_wall_stall_negative': 'build/roster-through-2-2/root49g-ryu-highcap-c-10-v0-mmc3/manifest.json',
        'RyuG_C_prefix_and_size_receipt': 'build/verification/ryu49g-cap-controller-c/actual-attempt-receipt.json',
        'MM_audio_V3_lossless_all_groups_strict_negative': 'build/verification/mm48-permanent-zp-writer-report-v3/all-writers-a.json',
        'MM_audio_V3_root_classification': 'build/verification/mm48-permanent-zp-writer-report-v3/root-classification-a.json',
    }
    missing_optional = []
    for key, name in refs.items():
        path = ROOT / name
        if key == 'SamusF_D_exact_late_Goomba_owner' and not path.exists():
            missing_optional.append(name)
            continue
        assert path.is_file(), name
        report['references'][key] = dict(path=name, sha256=sha(path))
    catalog_path = ROOT / 'build/verification/root49g-multirow-applied-a/applied-source-hashes.json'
    catalog = json.loads(catalog_path.read_text())
    assert len(catalog) == 404 and all(sha(ROOT / name) == digest for name, digest in catalog.items())
    total = sum((Path(parent) / name).stat().st_size
                for parent, _, names in os.walk(ROOT) for name in names)
    assert total < 30_000_000_000, total
    report.update(
        utc=datetime.now(timezone.utc).isoformat(), workspace_bytes=total,
        previous_progress=dict(path=str(prior.relative_to(ROOT)), sha256=sha(prior)),
        optional_classification_paths_not_found=missing_optional,
        root_native_jobs_running=[],
        agents={
            'megaman_bass': 'Preparing frozen source48 owner exchange via same-size GuestAudioBegin JMP and appended bank29 tail; root agreed local dead C/N/Z boundary only, full strict proof remains mandatory',
            'link_simon_ryu': 'Preparing bounded unchanged-C passive actual wall probe for missing source lower5px raise; no source defect certification before actual numeric/source receipt',
            'pit_rygar_sophia': 'Classifying E actual two floor Goomba defeats, subsequent airborne Paratroopa collision, and preparing next finite controller',
        },
    )
    report['limits'] += [
        'E actual controller killed the previous two floor Goombas with crouch beams, then died20218 against a different bouncing Paratroopa; exact prepared receipt pending. No source defect claimed.',
        'Ryu C literal9335 prefix exact; mounted highcap, then stalled929/Y160 and died15916. Potential missing source lower5px vertical grapple correction is under passive diagnostic preparation, not repaired or released.',
        'V3 complete all-group report contains72 strict CPU-model calls/10082 losslessly packed ordered writes. Samus logical state negative and Bill/Simon private snapshot negatives retained. Nine other groups pass7calls each, three stop after3calls. No new prototype qualification or shared audio change.',
    ]
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(path=str(out.relative_to(ROOT)), sha256=sha(out), workspace_bytes=total)))


if __name__ == '__main__':
    main()
