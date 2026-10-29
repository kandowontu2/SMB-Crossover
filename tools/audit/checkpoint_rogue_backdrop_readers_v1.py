"""Save the native backdrop result and immutable audio optimization, without ROM copies."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from checkpoint_roster_packets_v1 import ROOT, verify


def bound(path):
    path = Path(path).resolve()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return dict(path=str(path), bytes=path.stat().st_size, sha256=h.hexdigest())


def main():
    output = ROOT/'build/rogue-dawn-backdrop-readers-checkpoint-v1'
    output.mkdir(exist_ok=True)
    report = ROOT/'docs/qa/rogue-dawn-backdrop-native-and-readers-2026-10-29.json'
    assert not report.exists(), 'Append a successor; do not rewrite frozen evidence'
    handoffs = [
        (ROOT/'build/rogue-dawn-backdrop-v1/handoff.json',
         '502cce9718940bb1e08712bb6a1d33f5069ddcd6bafb166730b2aef77d04ce55'),
        (ROOT/'build/rogue-dawn-audio-readers-v6/handoff.json',
         '65a211947201749a607c46dcf02a0a8c8348cc611bec718cce92d2f7f29e8f01')]
    seen, public, extras = {}, {}, []
    for hp, digest in handoffs:
        assert bound(hp)['sha256'] == digest
        payload = json.loads(hp.read_text())
        verify(payload, seen)
        owned = hp.parent/'owned-files.json'
        for row in json.loads(owned.read_text())['public_files']:
            assert bound(row['path'])['sha256'] == row['sha256']
            public[row['path']] = row
        extras += [hp, owned]
    runs = []
    names = ['rogue-dawn-backdrop-native-easy-v1',
             'rogue-dawn-support-diagnostic-native-v1',
             'rogue-dawn-fresh-jump-native-v1']
    for name in names:
        folder = ROOT/'build/verification'/name
        ready, result, review, launch = [json.loads((folder/f).read_text())
            for f in ['ready.json', 'result.json', 'review.json', 'launch.json']]
        assert ready['ROM_sha256'] == '1241df0735eaf81a1c9db607c9a956b68add1bbad0416352d28c894c390df80c'
        assert not result['passed'] and result['zero_deaths']
        assert result['reason'] == 'finite frame bound'
        assert not launch['changed_inputs'] and launch['settings_before'] == launch['settings_after']
        assert result['full_frames'] == review['container']['full_frames']
        for path, digest in ready['bindings'].items():
            assert bound(path)['sha256'] == digest, path
            seen[path] = digest
        rows = [folder/n for n in ['ready.json', 'result.json', 'review.json', 'launch.json',
                                   'run.lua', 'inputs.csv', 'trace.csv', 'events.jsonl']]
        extras += rows
        if name.endswith('easy-v1'):
            extras.append(folder/'selected-whole-frames.png')
        if name == 'rogue-dawn-support-diagnostic-native-v1':
            extras.append(folder/'candidate-run.log')
        runs.append(dict(name=name, route_passed=False, reason=result['reason'],
            PPU_frames=result['frames'], completed_Main=result['completed_loops'],
            decoded_lossless_frames=result['full_frames'], min_SP=result['min_SP'],
            strict_guards_passed=True, zero_deaths=True,
            visually_viewed_selected_whole_frames=5 if name.endswith('easy-v1') else 0,
            result=bound(folder/'result.json'), review=bound(folder/'review.json'),
            capture_reference=bound(folder/'captures.nesppuv1')))
    data = dict(status='Native blue backdrop confirmed; three finite negative routes retained; reader CPU optimization source-qualified only',
        workspace_cap_bytes=70_000_000_000,
        backdrop_handoff=bound(handoffs[0][0]), reader_handoff=bound(handoffs[1][0]),
        runs=runs,
        visual_result='Root viewed all five selected wholeframes from the 7000-frame backdrop run. Overworld blue sky is restored; lives screen remains black. This is narrow backdrop confirmation, not an all-frame visual pass.',
        open_visuals='Frame663 contains separated midair body/shot pieces; cause is unclassified. Debug E091/M000 overlays remain. These are not silently accepted as final graphics.',
        route_result='Opening block acquisition still fails at X330..335/Y176. Actual foot probes see solid tile54/attribute41; running action1 persists with gravity26/0. A 3-on/4-off input-only retry also fails. Actual complete-Main/source diagnosis is active; do not attribute every failure to the controller or change physics merely to force a clear.',
        audio_measurement=dict(unit='Actual complete source-emulated NMI CPU cycles, not native FPS',
            heavy_before=17607, heavy_after=16335, quiet_before=7745, quiet_after=7408,
            source_comparison_cases=612, source_themes=6, source_effects=23,
            ordered_APU_and_state_exact=True, native_run=False),
        unchanged='Downloads current ac126 WIP; no canonical build promotion. Ordinary MMC3 d444 and MMC5 f4ffd exact in the source qualification.',
        scope='All compact lossless streams decoded structurally; only five selected wholeframes visually reviewed. No 1-1 clear, all-powerup, native audio-audibility or FPS claim.')
    report.write_text(json.dumps(data, indent=2)+'\n')
    extras += [report, Path(__file__).resolve(),
               ROOT/'tools/audit/rogue_dawn_native_prepare_v3.py',
               ROOT/'tools/audit/rogue_dawn_native_prepare_v4.py',
               ROOT/'tools/playthroughs/rogue_dawn_11_support_trace_v1.lua',
               ROOT/'tools/playthroughs/rogue_dawn_11_v3.lua']
    for p in extras:
        row = bound(p)
        public[row['path']] = row
    wrapper = dict(status=data['status'], candidate=bound(handoffs[1][0].with_name('candidate.nes')),
        report=bound(report), source_handoffs=[bound(hp) for hp, _ in handoffs],
        bindings=seen, actual_ASM_dependencies={}, owned_files=list(public.values()),
        limits=data['scope'])
    wrapper_path = output/'root-handoff.json'
    assert not wrapper_path.exists()
    wrapper_path.write_text(json.dumps(wrapper, indent=2)+'\n')
    subprocess.run([sys.executable, '-B', str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff', str(wrapper_path), '--name', 'rogue-native-backdrop-and-source-reader-optimization'],
        cwd=ROOT, check=True)
    progress = ROOT/'docs/qa/new-character-source-progress-2026-10-28.json'
    state = json.loads(progress.read_text())
    state['Rogue_backdrop_native_and_reader_optimization'] = bound(report)
    state['Rogue_owned_NMI_source']['status'] = (
        'Private source-NMI unit plus native-confirmed blue backdrop. Reader successor saves1272CPU heavy/337quiet in source NMI; native performance unrun. Opening block/jump responsiveness still fails discovery and is under actualMain diagnosis; no promotion.')
    progress.write_text(json.dumps(state, indent=2)+'\n')
    stage = [Path(p) for p in public] + [progress]
    checkpoint = ROOT/'docs/qa/checkpoints/2026-10-28/rogue-native-backdrop-and-source-reader-optimization'
    stage += [checkpoint/'root-review.json', checkpoint/'frozen-source-packet.zip']
    # This is a precise list for the root's later git action, never git add .
    (output/'public-stage-files.json').write_text(json.dumps([str(p) for p in stage
        if p.is_relative_to(ROOT/'src') or p.is_relative_to(ROOT/'tools')
        or p.is_relative_to(ROOT/'docs')], indent=2)+'\n')
    print(json.dumps(dict(report=bound(report), source_bindings=len(seen),
        public_stage_manifest=str(output/'public-stage-files.json'))))


if __name__ == '__main__':
    main()
