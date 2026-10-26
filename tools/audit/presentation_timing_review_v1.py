"""Independently inspect saved DMA/deadline records and decode actual PPU frames."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    result = json.loads((a.packet/'result.json').read_text(encoding='utf-8'))
    receipt = json.loads((a.packet/'native-receipt.json').read_text(encoding='utf-8'))
    assert result['passed'] and receipt['passed'] and receipt['result'] == result
    rows = [json.loads(s) for s in (a.packet/'timing.jsonl').read_text(encoding='utf-8').splitlines()]
    dmas = [r['DMA'] for r in rows if r['kind'] == 'DMA-complete']
    enables = [r for r in rows if r['kind'] == 'render-enable']
    assert len(dmas) == result['completed_DMAs'] and len(enables) == result['scoped_enables']
    assert [r['id'] for r in dmas] == list(range(1, len(dmas)+1))
    for d in dmas:
        assert d['completed_writes'] == 256 and d['source'] == d['hardware']
        assert len(d['source']) == 256 and d['mask'] & 24 == 0 and d['end_mask'] & 24 == 0
    for e in enables:
        line, dot = e['ppu']['scanline'], e['ppu']['dot']
        assert e['safe'] and (241 <= line <= 260 or line == -1 and dot <= 274)
    with (a.packet/'direct-index.csv').open(encoding='utf-8', newline='') as f:
        index = list(csv.DictReader(f))
    assert [int(r['ppuFrame']) for r in index] == list(range(176, 451))
    assert all(int(r['pixels']) == 61440 for r in index)
    assert (a.packet/'direct.argb').stat().st_size == len(index)*245760
    pixels = np.memmap(a.packet/'direct.argb', dtype=np.uint8, mode='r', shape=(len(index), 240, 256, 4))
    selected = [184, 194, 204, 371, 372, 373, 403, 404]
    sheet = Image.new('RGB', (1024, 520), '#202020')
    draw = ImageDraw.Draw(sheet)
    frame_hashes = {}
    for n in range(176, 451):
        rgb = np.asarray(pixels[n-176][:, :, [2, 1, 0]])
        frame_hashes[n] = hashlib.sha256(rgb.tobytes()).hexdigest()
        if n in selected:
            i = selected.index(n)
            image = Image.fromarray(rgb)
            image.save(a.output/f'frame-{n:06d}.png')
            x, y = i % 4*256, i // 4*260
            draw.text((x, y), f"{result['ROM_sha256'][:8]} actual {n}", fill='white')
            sheet.paste(image, (x, y+20))
    sheet.save(a.output/'selected-actual-frames.png')
    (a.output/'all275-RGB-hashes.json').write_text(json.dumps(frame_hashes, indent=2)+'\n', encoding='utf-8')
    files = {a.packet/n for n in ['direct.argb', 'direct-index.csv', 'timing.jsonl', 'native-receipt.json', 'result.json']}
    files |= {p for p in a.output.iterdir() if p.is_file()}
    proof = dict(passed=True, native_run=True, adopted=False, ROM_sha256=result['ROM_sha256'],
                 independent_full256_DMA_checks=len(dmas), independent_all_disabled=True,
                 scoped_enable_checks=len(enables), conservative_deadline_failures=0,
                 IRQ31_checks=result['IRQ31_checks'], NMI_AXY_SP_5SMC_checks=result['NMI_checks'],
                 actual_lossless_frames=len(index), actual_frame_range=[176, 450],
                 selected_actual_wholeframes=selected,
                 frame372_enable=[e for e in enables if e['ppu']['frame'] == 372],
                 frame372_DMA=[{k:v for k,v in d.items() if k not in ['source', 'hardware']} for d in dmas if d['complete']['frame'] == 372],
                 bindings={str(p):sha(p) for p in sorted(files)}, tool_sha256=sha(__file__),
                 limits='Finite actual MegaEasy450 integrity/hardware/deadline checks. Selected image review is separate; no all-menu/whole-route/all-roster/pressure/shot-fairness/adoption claim.')
    (a.output/'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ['passed', 'ROM_sha256', 'independent_full256_DMA_checks', 'actual_lossless_frames', 'frame372_enable']}))


if __name__ == '__main__':
    main()
