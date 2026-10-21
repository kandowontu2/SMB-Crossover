"""Review actual unseeded mushroom recordings without claiming full clears."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/verification/root49s2-mario-luigi-pickups-b'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dest = OUT / 'actual-review.json'
    assert not dest.exists()
    results = []
    for char, name in [(0, 'mario'), (8, 'luigi')]:
        p = R / f'build/roster-through-2-2/root49s2-{name}-pickup-b-{char}-v0-mmc3'
        m = json.loads((p / 'manifest.json').read_text())
        v = json.loads((p / 'review.json').read_text())
        observation = json.loads((p / 'pickup-observation-summary.json').read_text())
        assert m['controller_only'] and not m['memory_or_register_writes']
        assert m['rom_sha256'] == 'a2a4533de2f9416ff5c5722430376eced65bf532aac3f0d564f25afd13c65dc8'
        assert m['result']['failure'] == 'frame limit' and m['result']['deaths'] == 0
        assert not m['verified_through_2_2'] and not m['recording_verified']
        assert m['recording_metadata']['passed'] and (p / 'native.avi').exists()
        assert v['every_recorded_frame_decoded'] and v['decoded_video_frames'] == 2199
        flags = ['split_timing_candidates', 'lag_chr_change_candidates', 'motion_candidates',
                 'video_vertical_shift_candidates', 'video_background_flash_candidates',
                 'audio_events_needing_priority_or_audible_review', 'illegal_guest_native_stomps']
        assert all(not v[k] for k in flags)
        transitions = list(observation['transitions'].values())
        assert len(transitions) == 1 and transitions[0]['oldPower'] == 0 and transitions[0]['newPower'] == 1
        assert observation['spawnSeen'] and transitions[0]['spawnSeen']
        rows = list(csv.DictReader((p / 'pickup-observation.csv').open()))
        cues = [r for r in csv.DictReader((p / 'events.csv').open())
                if r['event'] == 'sfx-0104' and int(r['value']) & 32]
        assert cues
        cue = int(cues[0]['frame'])
        mushrooms = []
        for row in rows:
            for actor in row['actors'].split(';'):
                if actor:
                    slot, flag, ident, state, x, y = map(int, actor.split(':'))
                    if ident == 0x2e:
                        mushrooms.append(dict(frame=int(row['frame']), slot=slot, flag=flag,
                                              state=state, x=x, y=y))
        assert mushrooms and mushrooms[0]['frame'] < cue
        assert max(t['y'] for t in mushrooms) > min(t['y'] for t in mushrooms) + 24
        assert int(rows[-1]['power']) == 1 and int(rows[-1]['size']) == 0 and int(rows[-1]['engine']) == 8
        growth = [r for r in rows if int(r['engine']) == 9]
        assert growth and int(growth[0]['frame']) == cue + 1
        assert len({(r['x'], r['y']) for r in growth}) == 1
        wanted = sorted({cue - 2, cue, cue + 1, cue + 8, cue + 16, cue + 24,
                         cue + 32, cue + 40, cue + 48, cue + 56, cue + 61, cue + 70})
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(p / 'playthrough.mp4'),
                               '-an', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        captures = {}
        frame = 0
        while True:
            raw = ff.stdout.read(256 * 240 * 3)
            if not raw:
                break
            assert len(raw) == 256 * 240 * 3
            frame += 1
            if frame in wanted:
                captures[frame] = Image.frombytes('RGB', (256, 240), raw)
        error = ff.stderr.read().decode()
        assert ff.wait() == 0, error
        assert len(captures) == len(wanted)
        sheet = Image.new('RGB', (4 * 256, 3 * 264), '#202020')
        draw = ImageDraw.Draw(sheet)
        for j, n in enumerate(wanted):
            x, y = j % 4 * 256, j // 4 * 264
            sheet.paste(captures[n], (x, y))
            draw.text((x + 4, y + 243), f'{name} video frame{n}; cue{cue}', fill='white')
        image = OUT / f'{name}-growth-contact.png'
        sheet.save(image)
        files = ['manifest.json', 'review.json', 'inputs.csv', 'pickup-observation.csv',
                 'pickup-observation-summary.json', 'events.csv', 'native.avi', 'playthrough.mp4']
        results.append(dict(character=char, run=str(p.relative_to(R)),
            first_native_mushroom=mushrooms[0], last_native_mushroom=mushrooms[-1],
            real_pickup_queue_frame=cue, actual_power_transition=transitions[0],
            observed_growth_frames=len(growth), growth_first=int(growth[0]['frame']),
            growth_last=int(growth[-1]['frame']), growth_position_unchanged=True,
            final_power=1, final_size=0, final_engine=8,
            selected_native_video_frames=wanted, contact_sheet=dict(path=str(image.relative_to(R)), sha256=sha(image)),
            references={n: sha(p / n) for n in files},
            automated_audio_events=v['audio_source_event_count'],
            automated_audio_events_with_voice_and_physical_writes=v['audio_events_with_voice_and_physical_writes']))
    report = dict(status='PASS_ORDINARY_MUSHROOM_PICKUP_AND_GROWTH_COMPONENTS',
        script_sha256=sha(__file__), cases=results,
        setup_RAM_writes=False, partial_native_capture_metadata_passed=True,
        full_route_clear_claim=False, final_recording_claim=False,
        limits='Intentional unchanged harness frame-limit endpoints. Every recorded frame decoded; contact sheets require visual inspection. Queue/voice/write checks do not establish source-waveform parity or human listening.')
    dest.write_text(json.dumps(report, indent=2) + '\n')
    print(str(dest), sha(dest))


if __name__ == '__main__':
    main()
