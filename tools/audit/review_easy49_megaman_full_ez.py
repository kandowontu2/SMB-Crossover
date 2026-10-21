"""Freeze actual EC Mega Man MMC3 full clear and the separate MMC5 transfer negative."""
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    out = V / 'root49-ec-megaman-full-ez.json'
    assert not out.exists()
    discovery = P / 'root49ew-megaman-exit-1-v0-mmc3'
    fixed = P / 'root49ex-megaman-fixed-1-v0-mmc3'
    negative = P / 'root49ey-megaman-m5-fixed-1-v0-mmc5'
    assert (discovery / 'trace.csv').read_bytes() == (fixed / 'trace.csv').read_bytes()
    assert (discovery / 'inputs.csv').read_bytes() == (fixed / 'inputs.csv').read_bytes()
    manifest = json.loads((fixed / 'manifest.json').read_text())
    result = manifest['result']
    assert manifest['verified_through_2_2'] and manifest['full_frame_audit']
    assert not manifest['memory_or_register_writes'] and not manifest['config']['record']
    assert result['cleared'] and result['all_six_stages'] and result['deaths'] == 0
    assert result['frames'] == 25571 and result['polls'] == 25570
    assert result['stage_entries']['1-2'] == 25547
    assert manifest['rom_sha256'] == sha(fixed / 'smb-crossover-mmc3.nes') == '1d1c0a1024b4cb84edf2b46dca01eec0b28e415ed56292c6a8010dcb7d177db4'
    trace = rows(fixed / 'trace.csv')
    render = rows(fixed / 'render.csv')
    assert len(trace) == 25571 and len(rows(fixed / 'inputs.csv')) == 25570
    assert all(int(r['behaviorVersion']) == 0 for r in render)
    next_stage = [r for r in trace if int(r['frame']) >= result['stage_entries']['1-2']]
    assert len(next_stage) == 25 and int(next_stage[-1]['x']) > int(next_stage[0]['x'])
    changes = [dict(frame=int(b['frame']), world=int(b['world']), level=int(b['level']),
        x=int(b['x']), y=int(b['y']), before=int(a['power']), after=int(b['power']))
        for a, b in zip(trace, trace[1:]) if a['power'] != b['power']]
    profiles = defaultdict(lambda: dict(audited_frames=0, frames_flagged_lag_nmi=0,
        max_sprites_on_scanline=0, frames_with_hardware_APU_activity=0))
    for row in render:
        p = profiles[row['world'] + '-' + row['level']]
        p['audited_frames'] += 1
        p['frames_flagged_lag_nmi'] += int(row['lagNmi'])
        p['max_sprites_on_scanline'] = max(p['max_sprites_on_scanline'], int(row['maxSprites']))
        p['frames_with_hardware_APU_activity'] += int(int(row['apuMask']) != 0)
    refs = {}

    def pin(p):
        refs[p.relative_to(R).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)

    for folder in (discovery, fixed, negative):
        for p in folder.iterdir():
            if p.is_file():
                pin(p)
    for tag in ('root49-ep-megaman-22-water-a', 'root49-es-megaman-22-water-b', 'root49-et-megaman-22-water-c'):
        folder = P / 'search' / tag
        m = json.loads((folder / 'manifest.json').read_text())
        assert m['branch_coldboot_verified'] and m['winning_reusable_root']['ram_bytes_identical'] == 10240
        assert sha(folder / 'winning-inputs.csv') == m['winning_inputs_sha256']
        for name in ('manifest.json', 'winning-inputs.csv', 'winning-target.lua', 'coldboot-verified.json'):
            pin(folder / name)
    m5 = json.loads((negative / 'manifest.json').read_text())
    assert m5['rom_sha256'] == sha(negative / 'smb-crossover-mmc5.nes') == 'bccff505f56396a14cd7b64036d75071092b34c5d3accbf7fc1dd2e9548ca65b'
    assert m5['result']['failure'] == 'death' and m5['result']['frames'] == 1725
    assert not m5['verified_through_2_2'] and m5['full_frame_audit']
    m5_trace = rows(negative / 'trace.csv')
    columns = [n for n in trace[0] if n not in ('cycle', 'nmiSkipped')]
    diffs = [dict(frame=int(b['frame']), fields={k: [a[k], b[k]] for k in columns if a[k] != b[k]})
        for a, b in zip(trace, m5_trace) if any(a[k] != b[k] for k in columns)]
    live_diffs = [d for d in diffs if d['frame'] >= 541]
    report = dict(status='PASS_EC_MMC3_FIXED_FULL_2_2_CLEAR_MMC5_TRANSFER_NEGATIVE_RETAINED',
        script_sha256=sha(__file__), actual_EC_MMC3_ROM_sha256=manifest['rom_sha256'],
        full_MMC3_fixed_result=result, exact_discovery_trace_bytes=True,
        exact_all21_trace_fields_and25570_controller_polls=True,
        actual_behavior='Easy0, MegaMan1, outlinesOff; passive identity guard retained',
        real_next_stage_controls=dict(frames=25, start_x=int(next_stage[0]['x']), end_x=int(next_stage[-1]['x'])),
        natural_power_transitions=changes, full_render_profiles=dict(profiles),
        full_render_frames=len(render), actual_hardware_audio_events=len(rows(fixed / 'audio-events.csv')),
        MMC5_transfer=dict(result=m5['result'], first_gameplay_difference=live_diffs[0],
            differing19field_frames=len(live_diffs), scoped_transfer_negative=True,
            actual_native_injury_owner_not_captured=True,
            interpretation='A fixed MMC3 timing tape does not clear MMC5; no source collision defect inferred from this negative.'),
        final_integrated_runtime_not_replayed=True, final_recording=False,
        every_weapon_upgrade_claim=False, source_pixel_waveform_identity_claim=False,
        full_frame_audit_is_not_independent_perceptual_frame_by_frame_video_review=True,
        runtime_changes=False, main_changed=False, accepted_release=False, goal_complete=False,
        references=refs)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), report['MMC5_transfer']['first_gameplay_difference'])


if __name__ == '__main__':
    main()
