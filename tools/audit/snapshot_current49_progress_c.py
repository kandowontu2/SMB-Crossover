"""Record current, qualified continuation evidence without changing any inputs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root-current49-progress-c.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    catalog_path = ROOT / 'build/verification/root49g-multirow-applied-a/applied-source-hashes.json'
    catalog = json.loads(catalog_path.read_text())
    assert len(catalog) == 404
    assert all(sha(ROOT / name) == digest for name, digest in catalog.items())
    prior = ROOT / 'build/verification/root-current49-progress-b.json'
    report = json.loads(prior.read_text())
    additions = {
        'SamusF_C_actual_support_negative': 'build/verification/agent49f-samus-support-controller-d/actual-c-receipt.json',
        'SamusF_D_later_2_1_negative': 'build/roster-through-2-2/root49f-samus-support-live-d-2-v0-mmc3/manifest.json',
        'RyuG_B_clears_1_2_later_1_3_negative': 'build/roster-through-2-2/root49g-ryu-redkoopa-b-10-v0-mmc3/manifest.json',
        'MM_audio_8_streams_16008_strict_calls': 'build/verification/mm48-native-permanent-zp-cpu-proof-a/root-stream-batch-a.json',
        'MM_audio_control6513_strict_negative': 'build/verification/mm48-native-permanent-zp-cpu-proof-a/controls-a.negative.json',
        'MM_audio_Samus_actual_foreign_writers': 'build/verification/mm48-permanent-zp-samus-writer-repro-a/samus-writers-b.json',
        'MM_audio_original_probe_logger_negative': 'build/verification/mm48-permanent-zp-samus-writer-repro-a/samus-writers-a.log',
        'MM_audio_probe_v2_bound': 'build/verification/mm48-permanent-zp-samus-writer-repro-a/probe-v2-freeze.json',
        'MM_audio_all_groups_report_budget_negative': 'build/verification/mm48-permanent-zp-samus-writer-repro-a/all-writers-a.log',
    }
    # Optional classification names are not silently substituted. Record their
    # absence separately; all mandatory native/CPU receipts must exist.
    optional = {'SamusF_C_actual_support_negative'}
    absent = []
    for key, name in additions.items():
        path = ROOT / name
        if not path.exists() and key in optional:
            absent.append(name)
            continue
        assert path.is_file(), name
        report['references'][key] = {'path': name, 'sha256': sha(path)}
    total = 0
    for parent, _, files in os.walk(ROOT):
        for name in files:
            total += (Path(parent) / name).stat().st_size
    assert total < 30_000_000_000, total
    report.update(
        utc=datetime.now(timezone.utc).isoformat(),
        workspace_bytes=total,
        current404_source_exact=True,
        source_catalog_sha256=sha(catalog_path),
        previous_progress={'path': str(prior.relative_to(ROOT)), 'sha256': sha(prior)},
        optional_classification_paths_not_found=absent,
        root_native_jobs_running=[],
        agents={
            'megaman_bass': 'Host-only compact all-group writer report and ownership repair preparation; no new CPU/native execution authorized to agent',
            'link_simon_ryu': 'Host-only actual controllerB combat milestones and later1-3 death review; next bounded controller preparation',
            'pit_rygar_sophia': 'Host-only actual controllerD later2-1 death review; next bounded controller preparation',
        },
        limits=[
            'Accepted release remains48. Shared404 runtime sources and built ROMs remain provisional49G, exact to frozen catalog.',
            'G staged761 pass means759 unchanged full-run cases plus2 guarded outline cases; original760pass+1 alias-hook failure retained. No single full761-run claim.',
            'Samus accepted48 full2-2 clear independently replayed. F controllerD passes earlier2-1 bank section, later dies20006; no new full clear or ROM defect claimed.',
            'Ryu G controllerB clears1-2 after grounded combat, dies9403in1-3; later cause under review. No final current full clear claimed.',
            'Isolated audio prototype passed16008 strict stream calls and520 smoke calls. Controls fail6513 on firstSamus switch-away: native bank15 directSTA EC/ED corrupts proposed permanent MM3 state. Prototype remains unapplied and unqualified.',
            'Original diagnostic logger negative retained; V2 changes hash-helper Path conversion only. Three-call V2 preserves strict failure with actual writer bytes. All-group report exceeded frozen2MB output budget and wrote no JSON; no all-group result claimed.',
            'Dense MMC5 lag, complete14-character ordinary routes, all weapons/upgrades/source fidelity/AV and final recordings remain open.',
            'Workspace stays below30GB; all routes/native evidence/negatives retained. No prohibited route cleanup repeated.',
        ],
    )
    OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'path': str(OUT.relative_to(ROOT)), 'sha256': sha(OUT), 'workspace_bytes': total}))


if __name__ == '__main__':
    main()
