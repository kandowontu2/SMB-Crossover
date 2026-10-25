"""Index affected-controller evidence, frame suspects and sampled decoder images."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image, ImageDraw
from check_tmnt_render_oa import load, location

ROOT = Path(__file__).resolve().parents[2]


def rows(path):
    return list(csv.DictReader(path.open()))


def active(row):
    return row.get('world') == row.get('level') == '0' and row.get('engine') == '8' and row.get('mode') == '1' and row.get('task') == '3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_difference(before, after, fields):
    for i, (old, new) in enumerate(zip(before, after)):
        diff = {k: dict(accepted=old[k], private_proposal=new[k]) for k in fields if old[k] != new[k]}
        if diff:
            frame = int(new['frame'])
            return dict(frame=frame, seconds_at_60Hz=frame/60, fields=diff,
                        accepted=before[max(0, i-2):i+3], private_proposal=after[max(0, i-2):i+3])
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--folder', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    a = p.parse_args()
    out, d = a.folder.resolve(), a.archive.resolve()
    assert not out.is_relative_to(ROOT)
    proof = json.loads((out/'proof.json').read_text())
    bundle = load(Path(proof['rom']))
    irq_bank = (location(bundle, 'IrqScrollSplit')-16)//8192
    baseline = d/'zelda2-terrain-candidate-v4'
    index = dict(ROM_sha256=proof['ROM_sha256'], private_proposal=True, goal_complete=False,
                 native_discoveries=len(proof['runs']), unique_identities=len({r['identity'] for r in proof['runs']}),
                 all37_identities_covered=False, independent_PPU_replays=0, every_item_covered=False,
                 source_fidelity_qualified=False, lag_free_qualified=False, every_graphics_frame_visually_reviewed=False,
                 scope='Six affected native controller discoveries only. Samples use asynchronous decoder screenshots and are not physical PPU replay proof. Retained actual CHR and visible scroll split logs are independently indexed. Prior f00 results serve only as a comparison, not candidate qualification.',
                 accepted_baseline_ROM_sha256='f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23', runs=[])
    for run in proof['runs']:
        name, mode = run['identity'], run['mode']
        folder = Path(run['folder'])
        group = 'native-routes-v3' if name == 'zelda2' else ('native-controls-v2' if name == 'samus' else 'native-controls-v1')
        old = baseline/group/(name+'-'+mode)
        before, after = rows(old/'trace.csv'), rows(folder/'trace.csv')
        old_m, new_m = [json.loads((f/'manifest.json').read_text()) for f in [old, folder]]
        fields = ['world', 'level', 'area', 'x', 'y', 'yHigh', 'state', 'vx', 'vy', 'power', 'engine', 'mode', 'task', 'lives', 'camera', 'buttons']
        first = first_difference(before, after, fields)
        first_nmi = first_difference(before, after, ['nmiSkipped'])
        visible = [r for r in rows(folder/'scroll-writes.csv') if active(r) and r['screenDisabled'] == '0' and r['renderingEnabled'] == '1']
        bad_splits = [r for r in visible if r['scanline'] != '31' or int(r['writerBank']) != irq_bank]
        render = [r for r in rows(folder/'render.csv') if active(r)]
        old_render = [r for r in rows(old/'render.csv') if active(r)]
        screenshots = sorted((folder/'frames').glob('*.png'))
        active_trace = [r for r in after if active(r)]
        choices = [screenshots[min(range(len(screenshots)), key=lambda i: abs(int(screenshots[i].stem)-int(active_trace[round(j*(len(active_trace)-1)/15)]['frame'])))] for j in range(16)] if active_trace and screenshots else []
        sheet = Image.new('RGB', (1024, 1040), (24, 28, 36))
        draw = ImageDraw.Draw(sheet)
        for j, screenshot in enumerate(choices):
            with Image.open(screenshot) as im:
                sheet.paste(im.convert('RGB'), (j%4*256, j//4*260+20))
            draw.text((j%4*256+3, j//4*260+3), f'{name} {mode} decoder f{int(screenshot.stem)}', fill='white')
        sheet_path = out/(name+'-'+mode+'-sampled-decoder.png')
        sheet.save(sheet_path)
        item = dict(identity=name, mode=mode, source_mode=run['source_mode'], passed=run['passed'],
                    route_folder=str(folder), discovery_manifest_sha256=sha(folder/'manifest.json'),
                    result=run['result'], motion=run['motion'], chr_commit=run['chr_commit'],
                    actual_symbol_value_changes=[r for r in run['actual_symbol_bindings'] if r['old'] != r['actual']],
                    accepted_comparison_folder=str(old), harness_identical=old_m['harness_sha256'] == new_m['harness_sha256'],
                    first_gameplay_trace_difference=first, first_nmi_counter_difference=first_nmi,
                    visible_scroll_split=dict(passed=bool(visible) and not bad_splits, expected_scanline=31,
                                              expected_writer_bank=irq_bank, checks=len(visible), first_bad=bad_splits[:8]),
                    active_video_frames=len(render), active_lag_nmi_video_frames=sum(r['lagNmi']=='1' for r in render),
                    accepted_active_video_frames=len(old_render), accepted_active_lag_nmi_video_frames=sum(r['lagNmi']=='1' for r in old_render),
                    timing_comparison_limit='Routes can diverge after the first timing difference; these are not matched-input performance benchmarks.',
                    sampled_decoder_sheet=str(sheet_path), sampled_decoder_frames=[int(p.stem) for p in choices],
                    sampled_decoder_warning='Asynchronous decoder screenshots; no exact PPU frame attribution or exhaustive visual-review claim.')
        index['runs'].append(item)
    index['discovery_checks_passed'] = all(r['passed'] and r['visible_scroll_split']['passed'] for r in index['runs'])
    (out/'coverage-index.json').write_text(json.dumps(index, indent=2)+'\n')
    print(json.dumps(dict(ROM_sha256=index['ROM_sha256'], discoveries=index['native_discoveries'],
                          discovery_checks_passed=index['discovery_checks_passed'], output=str(out/'coverage-index.json'))))


if __name__ == '__main__':
    main()
