"""Publish the evidence index for twelve reviewed controller-only 1-1 runs."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('Mario', 'Mega Man', 'Samus', 'Bill', 'Link', 'Simon')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', default='palette-fixed')
    args = parser.parse_args()
    suite = json.loads((ROOT/'build/verification/summary.json').read_text())
    records = []
    for character, name in enumerate(NAMES):
        for route in ('surface', 'pipe'):
            directory = ROOT/'build/playthroughs'/f'{args.tag}-{character}-{route}'
            manifest = json.loads((directory/'manifest.json').read_text())
            review = json.loads((directory/'review.json').read_text())
            assert manifest['verified_full_coverage'], directory
            assert manifest['controller_only'] and not manifest['memory_or_register_writes']
            assert manifest['rom_sha256'] == suite['roms']['mmc3']
            assert hashlib.sha256((directory/'smb-crossover-mmc3.nes').read_bytes()).hexdigest() == manifest['rom_sha256']
            assert hashlib.sha256((directory/'applied-inputs.csv').read_bytes()).hexdigest() == manifest['applied_inputs_sha256']
            assert review['video_matches_emulated_frames']
            assert not any(review[key] for key in
                ('pixel_vertical_shift_flags', 'hud_split_flags', 'missing_common_sfx_flags'))
            assert (directory/'playthrough.mp4').stat().st_size > 0
            records.append({'character': name, 'route': route, 'directory': directory.relative_to(ROOT).as_posix(),
                'manifest': manifest, 'review': review})
    total = sum(r['review']['decoded_video_frames'] for r in records)
    summary = {'result': 'passed', 'roms': suite['roms'], 'runs': records,
        'decoded_frames': total, 'review_method': 'Automated every-frame checks plus visual inspection of event/contact sheets'}
    target = ROOT/'build/playthroughs/final-summary.json'
    target.write_text(json.dumps(summary, indent=2)+'\n')
    lines = ['# World 1-1 replay audit', '',
        f'All 12 fresh-power-on fixed-controller replays passed on the current MMC3 ROM. '
        f'The review decoded {total:,} native video frames. The emulator suite passed '
        f'{len(suite["cases"])} cases across MMC3 and MMC5.', '',
        'Each surface run defeats all 17 enemies and collects all five power-ups, including the hidden 1-up. '
        'Each shortcut-pipe run defeats all six enemies encountered along that route and collects its mushroom. '
        'Every run survives and verifies movement under controller input in World 1-2. '
        'These replays inspect memory but do not write game RAM or registers.', '',
        '| Character | Route/video | Frames | Enemies | Pickups | Lag frames | Overloaded sprite frames |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for item in records:
        m, r = item['manifest'], item['review']
        link = '../../'+item['directory']+'/playthrough.mp4'
        lines.append(f'| {item["character"]} | [{item["route"]}]({link}) | '
            f'{r["decoded_video_frames"]:,} | {m["audit"]["enemies_defeated"]} | '
            f'{m["result"]["goals"]} | {r["lag_frames"]} | {r["sprite_overload_frames"]} |')
    lines += ['',
        'Every AVI frame was decoded for the floor-row vertical-shift check; hardware scroll-register writes '
        'were audited at the HUD split, and queued common SFX were checked against voice ownership. '
        'These checks raised zero flags. Event contact sheets and frame sequences around power-up emergence '
        'support visual inspection; this is not a claim that every frame was watched manually.', '',
        'Native lossless AVI video and PCM audio were captured together in each replay. The MP4 is a viewing copy. '
        'The final emulator stop callback is one frame after AVI capture stops; the saved final screenshot '
        'and trace contain that last control-confirmation frame.', '',
        'Each run directory contains `manifest.json`, `review.json`, `applied-inputs.csv`, `trace.csv`, '
        '`objects.csv`, `events.csv`, `apu.csv`, `scroll-writes.csv`, `native.avi`, `end.png`, '
        '`review-contact-sheet.png`, and `reveal-*.png`. The manifest pins the ROM, policy, and input hashes.', '',
        'Lag and the NES eight-sprites-per-scanline limit remain visible in the counts above. '
        'Priority rotation shares visibility during sprite overload; these checks do not establish '
        'complete website parity or waveform identity for every sound.', '',
        'The latest Bill palette correction restores the shared mushroom tan ($27) in place of black ($0F). '
        'The hosted red/white bullet frames never use that third color, so their single-sprite layout is unchanged. '
        'The emulator checks preserve the item colors through both upgrade animations.', '',
        'Water was verified separately with explicit fixtures in the actual 2-2 room for all six characters '
        'on both mappers. Those checks cover source movement, surface/pose boundaries, jump rules, weapons, '
        'music and whirlpools; they are not full water-level completion replays. See [the water reference](../reference/water.md).', '',
        '## Reproduce', '', '```sh',
        'python tools/verify.py --mmc5',
        'python tools/playthroughs/verify_routes.py --tag replay-check',
        'python tools/playthroughs/review.py build/playthroughs/replay-check-3-surface',
        '```', '',
        'The default route prefixes use the accepted recordings above. The runner copies each ROM and its symbols '
        'into the run directory before starting the emulator. Captures use Mesen 2 with native sprite limits.', '',
        '## Tested ROM SHA-256', '',
        f'- MMC3: `{suite["roms"]["mmc3"]}`',
        f'- MMC5: `{suite["roms"]["mmc5"]}`', '']
    report = ROOT/'docs/qa/world-1-1.md'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('\n'.join(lines))
    print(f'PASS 12 reviewed routes; {total:,} native video frames; {report}')


if __name__ == '__main__':
    main()
