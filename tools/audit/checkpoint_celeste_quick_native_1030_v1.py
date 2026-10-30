"""Archive bounded native milestones and source bindings, excluding game ROMs."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
Q = R / 'docs/qa/checkpoints/2026-10-30'
ALLOW = {'.s', '.inc', '.cfg', '.json', '.py', '.lua', '.patch', '.md',
         '.chr', '.png', '.csv', '.jsonl', '.log', '.nesppuv1'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, data):
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + '\n')


def verify(p, expected):
    assert sha(p) == expected, p
    j = json.loads(p.read_text())
    for f, h in j['bindings'].items():
        assert sha(f) == h, f
    return j


def archive(out, files, receipt):
    assert not out.exists(), out
    out.mkdir(parents=True)
    files = sorted(set(files) | {Path(__file__).resolve()})
    target = out / 'source-and-native-evidence.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        for p in files:
            assert p.is_file() and p.is_relative_to(R) and p.suffix.lower() in ALLOW, p
            assert not p.read_bytes().startswith(b'NES\x1a'), p
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for n in z.namelist():
            assert hashlib.sha256(z.read(n)).hexdigest() == sha(R / n), n
    receipt.update(archive_sha256=sha(target), archive_bytes=target.stat().st_size,
                   archive_members=len(files), all_members_verified=True,
                   no_ROM_object_debug_files=True, root_tool_sha256=sha(__file__))
    save(out / 'receipt.json', receipt)
    print(json.dumps(dict(checkpoint=out.name, bytes=target.stat().st_size,
                         members=len(files))))


def main():
    p = R / 'build/current-celeste-easy-11-1030-v4'
    packet = verify(p / 'native-packet.json',
                    '3017d4cf20a8b44f0990ae99228b36c0b1af2de7919495ae6852425a63f33424')
    assert sha(packet['ROM']) == 'a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48'
    root = json.loads((p / 'root-review.json').read_text())
    assert root['passed'] and root['frames'] == 3900 and root['zero_deaths']
    assert root['power_tiers_seen'] == [0, 1, 2] and root['selected_PPU_screens'] == 7
    assert sha(p / 'selected-whole-frames.png') == '535e3c4114e0dee7ab115f8b4259d50f36c625a6c603a74bd05d2214e1e205a0'
    visual = dict(reviewed_by='root', scope='Seven selected complete lossless PPU frames only.',
                  montage_sha256=sha(p / 'selected-whole-frames.png'),
                  frames=[242, 700, 718, 1654, 1751, 2713, 3900],
                  findings=['Small Celeste Mario body and native terrain/powerups appear coherent in these frames.',
                            'Flagpole and the subsequent controllable 1-2 scene render coherently.'],
                  obvious_corruption_in_selected_frames=False, every_frame_visual_review=False,
                  no_audio_cadence_hard_mode_or_full_roster_claim=True)
    save(p / 'root-visual-review.json', visual)
    files = {Path(f) for f in packet['bindings'] if Path(f).suffix in ALLOW}
    # Keep the dense lossless prefix and both timeout negatives; do not silently
    # replace them with the later successful sparse run.
    for version in range(1, 5):
        d = R / f'build/current-celeste-easy-11-1030-v{version}'
        files.update(f for f in d.iterdir() if f.is_file() and f.suffix in ALLOW)
        tool = R / f'tools/audit/current_character_route_1030_v{version}.py'
        assert tool.is_file()
        files.add(tool)
    files.add(R / 'tools/audit/prepare_sparse_character_observer_1030_v1.py')
    archive(Q / 'celeste-easy-current-natural-11', files,
            dict(status='CURRENT_INSTALLED_CELESTE_EASY_NATURAL_11_PASS',
                 ROM_sha256=packet['ROM_sha256'], verified_packet_bindings=len(packet['bindings']),
                 frames=3900, completed_loops=3886, controlled_1_2=True,
                 both_upgrades_and_earned_dash=True, small_only=True, cheats=False, deaths=0,
                 selected_lossless_screens=7, visual_review=visual,
                 budget_seconds=93.973, budget_bytes_at_guard_completion=809046,
                 prior_dense_1160_frame_and_sparse_1869_frame_timeouts_retained=True,
                 source_policy_and_gameplay_assertions_unchanged=True,
                 no_all_frames_visual_review_or_all_character_completion_claim=True))

    p = R / 'build/current-character-quick-cold-v12'
    source = verify(p / 'handoff.json',
                    'd89d5eb86f74ce201fd7c1a4c13f0e153361bc7b95e1dbd403a10538326b7bfa')
    n = p / 'native-qualified-physical-v3'
    native = verify(n / 'handoff.json',
                    'c110e3a922ac161bc32a4d9344c846468dc9f8a25d4af56d348f829403e555e1')
    d = p / 'native/cold-menu-game-v3'
    result = json.loads((d / 'result.json').read_text())
    assert result['passed'] and result['native']
    visual = dict(reviewed_by='root', scope='All four selected current physical-v3 native PNGs.',
                  images={f.name:sha(f) for f in d.glob('*.png')},
                  findings=['Quick Man body, three-shot fan and native terrain look coherent in the selected gameplay frames.',
                            'BUSTER appears above Quick Man in later gameplay frames: confirmed incorrect inherited inventory HUD.',
                            'The selected character name and SELECT CHANGE HERO instruction are crowded and need a menu layout review.'],
                  every_frame_visual_review=False, UI_hold=True, performance_hold=True)
    save(n / 'root-visual-review.json', visual)
    files = {p / 'handoff.json', n / 'handoff.json', n / 'root-visual-review.json'}
    for handoff in [source, native]:
        files.update(Path(f) for f in handoff['bindings'] if Path(f).suffix in ALLOW)
    for sub in ['native-prepared.json', 'native-fresh-guard-v2',
                'native-physical-guard-v3b', 'native/cold-menu-game-v1',
                'native/cold-menu-game-v2', 'native/cold-menu-game-v3']:
        item = p / sub
        if item.is_file():
            files.add(item)
        else:
            assert item.is_dir(), item
            files.update(f for f in item.rglob('*') if f.is_file() and f.suffix in ALLOW)
    for name in ['run_current_quick_cold_native_v12.py',
                 'run_current_quick_cold_native_fresh_v2.py',
                 'run_current_quick_cold_native_physical_v3.py']:
        files.add(R / 'tools/audit' / name)
    archive(Q / 'quick-current-cold-native-ui-performance-hold', files,
            dict(status='PRIVATE_NATIVE_COLD_SMOKE_PASS_UI_AND_PERFORMANCE_HOLD',
                 source_handoff_sha256=sha(p / 'handoff.json'),
                 native_handoff_sha256=sha(n / 'handoff.json'),
                 verified_source_bindings=len(source['bindings']),
                 verified_native_bindings=len(native['bindings']),
                 ROM_sha256='cbbf28b1f0fc37718c50f07389bf9258ca2868b79f3d7efe8f47f44a325fdee8',
                 actual_cold_loader_reads=18450, emulated_frames=525, game_frames=220,
                 gameplay_HP=40, genuine_QhUi_calls=0, gameplay_NmiSkipped=[28,166],
                 source_Main_profile=dict(calls=118, mean_CPU=28543.195, max_CPU=41079),
                 source_draw_profile=dict(calls=66, mean_CPU=2453.076),
                 selected_visual_review=visual, prior_two_fixture_negatives_retained=True,
                 native_smoke=True, cadence_qualified=False, admitted=False, installed=False,
                 excluded_compiled_payloads_recorded_in_original_binding_manifest=True))


if __name__ == '__main__':
    main()
