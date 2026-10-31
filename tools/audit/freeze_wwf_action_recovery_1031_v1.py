"""Freeze original WWF action timing, its art closure and bounded donor trace."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
S = R/'build/wwf-roster-source-review-v1'
N = R/'build/wwf-action-donor-native-1031-v1/discovery'
P = R/'build/wwf-action-vm-recovery-1031-v1'
O = R/'docs/qa/checkpoints/2026-10-31/wwf-action-source-recovery-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, q):
    assert not p.exists()
    p.write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8', newline='\n')


def main():
    assert not O.exists()
    d = json.loads((P/'controls.json').read_text())
    assert d['passed'] and len(d['cases']) == 66 and d['genuine_script_updates'] == 4224
    for p, digest in d['bindings'].items():
        assert sha(p) == digest, p
    art = json.loads((S/'wrestlers.json').read_text())
    frozen = json.loads((S/'handoff.json').read_text())
    assert sha(S/'wrestlers.json') == frozen['bindings'][str(S/'wrestlers.json')]
    keys = {(q['character'], q['group'], q['frame']): q for q in art['poses']}
    assert len(keys) == 195
    matched, rows = 0, []
    for case in d['cases']:
        episodes = []
        for s in case['sequence']:
            assert (case['character'], s['group'], s['pose']) in keys
            matched += 1
            state = tuple(s[k] for k in ['action', 'group', 'pose', 'direction'])
            if episodes and tuple(episodes[-1]['state']) == state:
                episodes[-1]['updates'] += 1
            else:
                episodes.append(dict(first_update=s['tick'], updates=1, state=state))
        rows.append(dict(character=case['character'], name=case['name'], source_input=case['input'],
            native_action=case['native_action'], actor_updates=64, source_video_frame_stride=2,
            episodes=episodes, CPU_cycles=[min(s['CPU_cycles'] for s in case['sequence']),
                                         max(s['CPU_cycles'] for s in case['sequence'])],
            original_APU_write_count=len(case['original_audio_writes'])))
    assert matched == 4224
    O.mkdir(parents=True)
    write(O/'action-art-contracts.json', dict(passed=True, original_renderer_poses=195,
        matched_VM_output_samples=matched, rows=rows,
        source_actor_identity_mapping=d['native_identity_layout'],
        limitations=d['limitations'],
        scope='Source action/pose/timing recovery, not precomputed playback as a replacement for the original VM. A host still needs real contact/eligibility and native script side effects.'))
    files = {p for p in N.rglob('*') if p.is_file()}
    files.update([P/'controls.json', P/'executed-PCs.json', S/'wrestlers.json',
        S/'native-action-directories-scripts.bin', S/'native-descriptors.bin', S/'handoff.json',
        R/'tools/audit/wwf_roster_source_review_v1.py',
        R/'tools/audit/prepare_wwf_action_discovery_1031_v1.py',
        R/'tools/audit/wwf_action_vm_recovery_1031_v1.py', Path(__file__), O/'action-art-contracts.json'])
    assert len(files) < 64
    assert sum(p.stat().st_size for p in files) < 16777216
    assert len([p for p in files if p.suffix == '.png']) == 4
    assert all(p.suffix.lower() in ['.py', '.lua', '.json', '.csv', '.log', '.png', '.bin'] for p in files)
    archive = O/'source-and-bounded-donor.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(files):
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in files:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    assert archive.stat().st_size < 4194304
    write(O/'handoff.json', dict(status='ORIGINAL_WWF_ACTION_VM_SOURCE_RECOVERY_NO_HOST_UNLOCK',
        source=True, native_original_game=True, native_host=False, playable_host=False,
        original_ROM=frozen['original_ROM_sha256'], source_script_updates=4224,
        controller_trace_dispatches=1076, wrestler_input_cases=66, matched_source_art_samples=matched,
        source_renderer_poses=195, root_reviewed_whole_PNGs=4, no_RAM_writes_in_native_run=True,
        notes=['Original USA ROM, not the older Mario-in-WWF build, is authoritative.',
               'The old frozen asset leaf has six changed external Mario-port build/documentation bindings. New ready.json records these; unchanged original ROM and required source assets are independently pinned.',
               'Native state actor0 uses descriptor2B; actor1 uses2A. Future ports must not reverse the selected wrestler/action table.',
               'Per-actor action VM ticks every other video frame. Native source has distinct A/B/combo scripts and animation timing for all six wrestlers.'],
        next=['Port genuine action interpreter with explicit host terrain/contact callbacks.',
              'Resolve two-palette body ownership and dynamic84-page art storage.',
              'Port/loop each original theme across all area types.',
              'Actual host menu/lives/movement/combat and1-1/every-powerup qualification.'],
        limits=d['limitations'], archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix(): sha(p) for p in sorted(files)}))
    (O/'README.txt').write_text('Original WrestleMania action recovery: one controller-only native USA-ROM run reaches the actual ring, captures1076 real E385 dispatches, four full frames and five2KiB initialized-state snapshots. Root reviewed all four frames. No RAM writes/video/frame forest. Using that initialized source state,66 explicit original-CPU input cases execute4224 genuine E2E8 actor updates. Every output group/pose resolves to one of the195 source-authentic renderer records.\n\nThe source has an important reversed selection layout: state actor0 uses character2B, actor1 uses2A; the donor observation CSV records raw2A/2B in its historically named identity columns. Per-actor scripts update every second video frame. The compact contract is an audit/reference, not a fabricated fixed playback implementation. Wrestling eligibility, contacts, ring-versus-platform adaptation, graphics/palette storage, music and the actual playable host remain unfinished. This checkpoint does not unlock the WWF roster.\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(passed=True, source_updates=4224, source_art_matches=matched,
                         archive_bytes=archive.stat().st_size, members=len(files))))


if __name__ == '__main__':
    main()
