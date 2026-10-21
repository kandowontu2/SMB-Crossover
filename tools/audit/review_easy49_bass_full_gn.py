"""Freeze the exact EL Bass MMC3 full replay and separate MMC5 transfer negative."""
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
    out = V / 'root49-el-bass-full-gn.json'
    assert not out.exists()
    discovery = P / 'root49gk-bass-live-9-v0-mmc3'
    fixed = P / 'root49gl-bass-fixed-9-v0-mmc3'
    negative = P / 'root49gm-bass-m5-fixed-9-v0-mmc5'
    assert (discovery / 'trace.csv').read_bytes() == (fixed / 'trace.csv').read_bytes()
    assert (discovery / 'inputs.csv').read_bytes() == (fixed / 'inputs.csv').read_bytes()
    m = json.loads((fixed / 'manifest.json').read_text())
    result = m['result']
    assert m['verified_through_2_2'] and m['full_frame_audit']
    assert not m['memory_or_register_writes'] and not m['config']['record']
    assert result['cleared'] and result['all_six_stages'] and result['deaths'] == 0
    assert result['frames'] == 26689 and result['polls'] == 26688
    assert result['stage_entries']['1-2'] == 26665
    assert m['rom_sha256'] == sha(fixed / 'smb-crossover-mmc3.nes') == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    trace, render = rows(fixed / 'trace.csv'), rows(fixed / 'render.csv')
    assert len(trace) == 26689 and len(trace[0]) == 21
    assert len(rows(fixed / 'inputs.csv')) == 26688
    assert all(int(r['behaviorVersion']) == 0 for r in render)
    identity = json.loads((fixed / 'identity.json').read_text())
    assert identity == dict(character=9, mode=0, controller_only=True)
    end = [r for r in trace if int(r['frame']) >= 26665]
    assert len(end) == 25 and end[0]['x'] == '40' and int(end[-1]['x']) > 40
    changes = [dict(frame=int(b['frame']), world=int(b['world']), level=int(b['level']),
        x=int(b['x']), y=int(b['y']), before=int(a['power']), after=int(b['power']))
        for a, b in zip(trace, trace[1:]) if a['power'] != b['power']]
    profiles = defaultdict(lambda: dict(audited_frames=0, flagged_lag_NMI_frames=0,
        max_sprites_on_scanline=0, frames_with_hardware_APU_activity=0))
    for r in render:
        z = profiles[r['world'] + '-' + r['level']]
        z['audited_frames'] += 1
        z['flagged_lag_NMI_frames'] += int(r['lagNmi'])
        z['max_sprites_on_scanline'] = max(z['max_sprites_on_scanline'], int(r['maxSprites']))
        z['frames_with_hardware_APU_activity'] += int(int(r['apuMask']) != 0)
    nm = json.loads((negative / 'manifest.json').read_text())
    assert nm['full_frame_audit'] and not nm['verified_through_2_2']
    assert nm['rom_sha256'] == sha(negative / 'smb-crossover-mmc5.nes') == '3161fa3d8eb002f9a98a7c29cac6347770d955252c49bd0337e5a13b93579d10'
    assert nm['result']['failure'] == 'death' and nm['result']['frames'] == 2279
    ntrace = rows(negative / 'trace.csv')
    fields = [k for k in trace[0] if k not in ('cycle', 'nmiSkipped')]
    differences = [dict(frame=int(b['frame']), fields={k: [a[k], b[k]] for k in fields if a[k] != b[k]})
        for a, b in zip(trace, ntrace) if int(b['frame']) >= 541 and any(a[k] != b[k] for k in fields)]
    assert differences
    assert len(rows(negative / 'mm-injury-owner.csv')) == 0
    refs = {}

    def pin(p):
        refs[p.relative_to(R).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)

    for folder in (discovery, fixed, negative):
        for p in folder.iterdir():
            if p.is_file():
                pin(p)
    for tag in ('root49-fg-bass-12-pipes-a', 'root49-fi-bass-13-first-gap-a',
                'root49-fl-bass-13-middle-a', 'root49-fn-bass-14-first-bars-a',
                'root49-fp-bass-14-middle-a', 'root49-fr-bass-21-first-stairs-a',
                'root49-fx-bass-21-middle-gap-a', 'root49-fz-bass-21-flying-fish-a',
                'root49-gb-bass-22-middle-fish-a', 'root49-ge-bass-22-coral-gap-a',
                'root49-gi-bass-22-tall-coral-a'):
        f = P / 'search' / tag
        d = json.loads((f / 'manifest.json').read_text())
        root = d['winning_reusable_root']
        assert d['branch_coldboot_verified'] and root['verified_coldboot']
        assert root['ram_bytes_identical'] == 10240 and not root['savestate_loads'] and not root['emulated_writes']
        assert sha(f / 'winning-inputs.csv') == root['inputs_sha256']
        for name in ('manifest.json', 'winning-inputs.csv', 'winning-target.lua', 'coldboot-verified.json'):
            pin(f / name)
    checkpoint = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(checkpoint) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    c = json.loads(checkpoint.read_text())
    assert len(c['source_hashes']) == 441
    assert all(sha(R / n) == h for n, h in c['source_hashes'].items())
    for b in c['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    pin(checkpoint)
    report = dict(status='PASS_EL_MMC3_BASS_FIXED_FULL_2_2_CLEAR_MMC5_TRANSFER_NEGATIVE_RETAINED',
        script_sha256=sha(__file__), fixed_result=result, actual_EL_MMC3_ROM_sha256=m['rom_sha256'],
        exact_all21_trace_fields_and26688_controller_polls=True,
        independent_ordinary_startup=True, active_behavior='Easy0, Bass9, outlinesOff; passive identity guard',
        real_next_stage_controls=dict(frames=25, start_x=40, end_x=int(end[-1]['x'])),
        natural_power_transitions=changes, physical_frame_render_profiles=dict(profiles),
        audited_render_frames=len(render), hardware_audio_event_rows=len(rows(fixed / 'audio-events.csv')),
        MMC5_transfer=dict(result=nm['result'], first19field_gameplay_difference=differences[0],
            differing19field_gameplay_frames=len(differences), actual_native_injury_callbacks=0,
            endpoint=ntrace[-1], interpretation='Same-tape timing transfer fails at a pit with no native hostile-injury receipt; no mapper/source collision defect inferred.'),
        current_EL_sources_and_eight_artifacts_rehashed=True,
        final_integrated_successor_not_replayed=True, final_recording=False,
        all_arsenal_or_every_powerup_claim=False, individual_fresh_jump_support_audit_complete=False,
        glitchless_or_source_pixel_waveform_identity_claim=False,
        full_frame_audit_is_not_independent_perceptual_frame_by_frame_video_review=True,
        runtime_changes=False, main_changed=False, accepted_release=False, goal_complete=False,
        references=refs)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], sha(out), report['real_next_stage_controls'], report['MMC5_transfer']['first19field_gameplay_difference'])


if __name__ == '__main__':
    main()
