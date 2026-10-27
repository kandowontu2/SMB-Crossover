"""Compare actual sound-menu note timing with normal assembled playback."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--negative', type=Path, required=True)
    args = parser.parse_args()
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    b = scoped_load(args.rom)
    result = json.loads((args.native/'regression-result.json').read_text())
    launch = json.loads((args.native/'launch.json').read_text())
    assert result['passed'] and launch['unchanged'] and launch['exit'] == 0
    assert launch['before'][str(args.rom.resolve())] == sha(args.rom)
    notes = list(csv.DictReader((args.native/'mario-notes.csv').open()))
    assert len(notes) >= 300
    q = Arena(b, 0)
    q.put(OperMode=1, AreaMusicQueue=1)
    for tick, row in enumerate(notes, 1):
        q.invoke('AudioUpdate')
        assert int(row['tick']) == tick
        for name, value in row.items():
            if name != 'tick':
                assert q.get(name) == int(value), (tick, name, q.get(name), value)
    playback = list(csv.DictReader((args.native/'playback.csv').open()))
    assert len(playback) == len({r['character'] for r in playback}) == 37
    assert all(int(r['ticks']) == int(r['nmis']) >= 270 and
               int(r['irq_calls']) == int(r['visible_scroll_writes']) == 0 and
               int(r['stable_frames']) == 30 for r in playback)
    # The retained controller-only diagnostic on dc21 exposed both symptoms.
    old = list(csv.DictReader((args.negative/'timing.csv').open()))
    old_first = next(r for r in old if r['hero'] == '0' and int(r['offset2']) == 2)
    assert int(old_first['note2']) == 115
    bad = [r for r in csv.DictReader((args.negative/'events.csv').open())
           if r['event'].startswith('PPU') and 0 <= int(r['scanline']) < 240]
    assert len(bad) == 7536
    report = dict(passed=True, ROM_sha256=sha(args.rom),
                  compared_normal_gameplay_Mario_ticks=len(notes),
                  compared_fields=list(notes[0])[1:],
                  sustained_characters=len(playback),
                  actual_audio_ticks=sum(int(r['ticks']) for r in playback),
                  static_pixel_samples_per_character=30,
                  gameplay_split_calls=0, visible_scroll_writes=0,
                  maximum_actual_NMI_cycles=max(int(r['max_nmi_cycles']) for r in playback),
                  retained_negative_first_note_frames=115, corrected_first_note_frames=9,
                  retained_negative_visible_scroll_writes=len(bad),
                  scope='Actual menu cadence and pixels for 37 overworld selections; '
                        'Mario note state equals ordinary assembled AudioUpdate each tick. '
                        'No all-song waveform-fidelity or full gameplay claim.',
                  screenshots=4, per_frame_files=0)
    (args.native/'independent-review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
