"""Freeze continuation evidence; this is progress, never a release acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'build/verification/root-current49-progress-f.json'
    assert not out.exists()
    prior = ROOT / 'build/verification/root-current49-progress-e.json'
    report = json.loads(prior.read_text())
    refs = {
        'MM_ownerC_smoke520': 'build/verification/mm48-owner-transfer-cpu-proof-a/smoke-a.json',
        'MM_ownerC_controls6580': 'build/verification/mm48-owner-transfer-cpu-proof-a/controls-a.json',
        'MM_ownerC_toSamus532': 'build/verification/mm48-owner-transfer-cpu-proof-a/ownership-to-samus-a.json',
        'MM_ownerC_streams16008': 'build/verification/mm48-owner-transfer-cpu-proof-a/streams-a.json',
        'MM_ownerC_ownership16404': 'build/verification/mm48-owner-transfer-cpu-proof-a/ownership-all-a.json',
        'MM_ownerC_native_plan_only': 'build/verification/mm48-owner-c-native-plan-a/frozen.json',
        'RyuH_isolated_build': 'build/verification/root49g-grapple-private-build-a/report.json',
        'RyuH_inherited_unit_applicability': 'build/verification/ryu49h-samus-unit-applicability-a/report.json',
        'RyuH_all_RAM_native_differential': 'build/verification/ryu49h-grapple-native-differential-a/report.json',
        'RyuH_ordinary_continuation': 'build/roster-through-2-2/root49h-ryu-C-continuation-a-10-v0-mmc3/manifest.json',
        'RyuH_ordinary_prefix_and_size': 'build/verification/ryu49h-continuation-a/actual-attempt-receipt.json',
        'Samus_crouch_independent_source_audit': 'build/verification/agent49f-samus-crouch-source-audit-a/freeze.json',
    }
    for key, name in refs.items():
        path = ROOT / name
        assert path.is_file(), name
        report['references'][key] = dict(path=name, sha256=sha(path))
    proof = ROOT / 'build/verification/mm48-owner-transfer-cpu-proof-a'
    counts = [json.loads((proof / name).read_text())['cases'] for name in
              ['smoke-a.json', 'controls-a.json', 'ownership-to-samus-a.json', 'streams-a.json', 'ownership-all-a.json']]
    assert counts == [520, 6580, 532, 16008, 16404] and sum(counts) == 40044
    catalog = json.loads((ROOT / 'build/verification/root49g-multirow-applied-a/applied-source-hashes.json').read_text())
    assert len(catalog) == 404 and all(sha(ROOT / name) == value for name, value in catalog.items())
    for folder, field in [('root-mm48-owner-transfer-build-a', 'source404_hashes'), ('root49g-grapple-private-build-a', 'source405_hashes')]:
        path = ROOT / 'build/verification' / folder
        build = json.loads((path / 'report.json').read_text())
        assert all(sha(path / 'source' / name) == value for name, value in build[field].items())
    total = sum((Path(parent) / name).stat().st_size
                for parent, _, names in os.walk(ROOT) for name in names)
    assert total < 30_000_000_000, total
    report.update(
        utc=datetime.now(timezone.utc).isoformat(), workspace_bytes=total,
        previous_progress=dict(path=str(prior.relative_to(ROOT)), sha256=sha(prior)),
        root_native_jobs_running=[],
        agents={
            'megaman_bass': 'Host-only executable first ownerC native observer preparation; all40044 CPU calls pass, native plan only so far',
            'link_simon_ryu': 'Host-only ordinaryH actual raise/departure and subsequent10140death review; no new source/native execution',
            'pit_rygar_sophia': 'Host-only coherent crouch fix with existing body14/terrain5/water15.5, independent ABI/native fixtures; fresh Down/Up water ordering gap retained explicitly',
        },
    )
    report['limits'] += [
        'OwnerC has40044 actual executed dual CPU calls PASS across five runs; to-Samus logical coverage overlaps full ownership. No40044unique-case claim. No ownerC native execution, waveform/performance acceptance or shared audio edits yet.',
        'Private RyuH M3/M5 change only342bytes inbank61, preserve every oldlabel and entire bank10. Both24case native components PASS; oldG has12expected raises failing plus12control passes permapper. Data-only differential checks all10240RAM bytes and every orderedwrite without excluded addresses; independent boot differences and13dead-stack cells remain explicit.',
        'RyuH inherits339412 bounded bank10 helper cases by actualclosure byteidentity, ZERO new model cases. That applicability does not cover new AfterMotion/helper behavior.',
        'OrdinaryH preserves9335 prior inputs and passes formerly stuck questionblock, reaches955/Y123 at9600, then dies10140in1-3. No full route clear claimed; actual next owner review pending.',
        'Independent sourceXML/AS audit confirms Samus crouch15.5NESpx vs runtime25; native integer projection top17/body15 and terrainprofile5 are proposed, not applied. Earlier broad no-ROM-bug interpretation of E is superseded only by additive evidence; old raw evidence remains.',
        'Samus water height update on fresh Down/Up can lag one update because current water check precedes form mutation. New proposal must expose this timing limitation; no full source water identity claim. At actual floor1222/Y176 both forms are submerged, so that limitation does not defeat the overhead-fish correction.',
        'Workspace remains below30GB; final recording headroom is currently insufficient. All routes/native negatives/raw proof evidence remain retained, and prohibited route cleanup was not repeated.',
    ]
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(path=str(out.relative_to(ROOT)), sha256=sha(out), workspace_bytes=total)))


if __name__ == '__main__':
    main()
