"""Preserve the reviewed private exit patch and its actual native outcomes."""
from pathlib import Path
import hashlib
import json
import zipfile

from checkpoint_roster_packets_v1 import verify

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT/'build/rogue-dawn-flagpole-v1'
REPORT = ROOT/'docs/qa/rogue-dawn-flagpole-2026-10-30.json'
DEST = ROOT/'docs/qa/checkpoints/2026-10-30/rogue-dawn-flagpole'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    assert not REPORT.exists() and not DEST.exists(), 'Preserve completed checkpoint'
    inputs = {}
    for name in ['handoff.json', 'build.json', 'controls.json']:
        path = UNIT/name
        data = json.loads(path.read_text())
        assert data['passed']
        verify(data, inputs)
        inputs[str(path)] = sha(path)
    controls = json.loads((UNIT/'controls.json').read_text())
    runs = []
    extras = [Path(__file__), ROOT/'tools/audit/run_mesen_output_v2.py']
    for version in [1, 2, 3]:
        folder = ROOT/f'build/verification/rogue-dawn-flagpole-native-easy-v{version}'
        ready = json.loads((folder/'ready.json').read_text())
        assert all(sha(p) == h for p, h in ready['bindings'].items())
        assert ready['ROM_sha256'] == sha(UNIT/'candidate.nes')
        inputs.update(ready['bindings'])
        budget = json.loads((folder/'capture-budget.json').read_text())
        assert budget['owned_process_only'] and not budget['violations']
        files = [p for p in folder.iterdir() if p.is_file()]
        assert len(files) <= 64
        assert sum(p.stat().st_size for p in files) < 600_000_000
        result = json.loads((folder/'result.json').read_text()) if (folder/'result.json').exists() else None
        if version == 1:
            assert result and not result['passed'] and result['reason'] == 'finite frame bound'
        elif version == 2:
            assert not result and (folder/'root-stop.json').exists()
        else:
            assert result and result['passed'] and result['zero_deaths']
            assert result['real_1_1_seen'] and result['real_1_2_control_updates'] >= 25
            assert result['actual_mode'] == 0 and result['cheats_off']
            review = json.loads((folder/'review.json').read_text())
            assert review['passed'] and not review['agent_visual_review']
        runs.append(dict(name=folder.name, result=result, outputs=[binding(p) for p in files],
                         scope='Controller-only exact candidate, normal eight sprites per scanline; selected images separately viewed.'))
        extras.extend(p for p in files if p.suffix in ['.json', '.lua', '.log', '.png', '.csv', '.jsonl'])
    extras.extend(UNIT.glob('*negative*.json'))
    extras.extend(UNIT.glob('*negative*.log'))
    for p in extras:
        inputs[str(p.resolve())] = sha(p)
    report = dict(status='Private source-qualified Rogue exit patch; actual Easy 1-1 clear to controlled 1-2; shared integration still open',
                  installed=False, ROM=binding(UNIT/'candidate.nes'),
                  parent=binding(ROOT/'build/rogue-dawn-side-v1/candidate.nes'),
                  implementation=dict(new_RAM=0, changed_bytes=213, source_solid_collision_unchanged=True,
                    actual_contact='Source center/radii sample genuine loaded block buffer; four-pixel shaft range; native flagpole transaction owns music, sound, score, enemy cleanup and alignment.',
                    automatic_motion='Actual SMB background collision resumes for automatic victory, pipe and death motion.',
                    source_layout='Existing A1 gate24B and selector15B retained; new A95 dispatchBEDD..BEFD and workerBF32..BFCC, frozen BF00..BF31 death descriptors unchanged.'),
                  CPU_checks={k:len(v) for k,v in controls['checks'].items()},
                  actual_native_runs=runs,
                  retained_negative_scope='V1 stale controller aimed beside question; V2 repeated the existing v5 top-of-row approach and was stopped by verified owned PID. V3 uses the previous physical-pickup/source-staircase v9 route. No product assertion was waived.',
                  visual_scope='Root viewed all seven selected whole frames and the checksum-verified eighth frame at actual engine4 flagpole contact; no all-frame/all-pixel/audio certification.',
                  open=['Shared full-roster admission', 'Hard-mode controller route', 'Every Rogue weapon/upgrade earned at least once',
                        'Shortcut pipe, other stage transitions, vine/coin/axe coverage',
                        'Victory presentation: automatic motion currently retains the most recent source animation pose',
                        'Performance optimization; native measured lag is retained, no 60 Hz claim'])
    REPORT.parent.mkdir(exist_ok=True, parents=True)
    REPORT.write_text(json.dumps(report, indent=2)+'\n')
    inputs[str(REPORT)] = sha(REPORT)
    DEST.mkdir(parents=True)
    members = {}
    excluded = {'.nes', '.dbg', '.lbl', '.map', '.exe', '.dll', '.mp4', '.wav', '.nesppuv1'}
    with zipfile.ZipFile(DEST/'frozen-source-packet.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path_string, expected in inputs.items():
            path = Path(path_string).resolve()
            assert sha(path) == expected
            if path.suffix in excluded or not path.is_relative_to(ROOT):
                continue
            data = path.read_bytes()
            member = path.relative_to(ROOT).as_posix()
            item = zipfile.ZipInfo(member, (2026, 10, 30, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(item, data)
            members[member] = expected
    with zipfile.ZipFile(DEST/'frozen-source-packet.zip') as archive:
        assert {name:hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()} == members
    proof = dict(status='Root-reviewed private source/native checkpoint; not installed or exposed as playable in shared build',
                 report=binding(REPORT), archive=binding(DEST/'frozen-source-packet.zip'),
                 verified_bindings=len(inputs), members=members, runtime_references=inputs)
    (DEST/'root-review.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(report=binding(REPORT), archive=proof['archive'], members=len(members))))


if __name__ == '__main__':
    main()
