"""Extract a finite actual-PPU contact/rise sequence; no emulator launch."""
from pathlib import Path
import csv
import hashlib
import json
from PIL import Image, ImageDraw

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
NATIVE = D/'bass-arm-question-boundary-v1/native-ready-v3/native'
OUTPUT = D/'bass-arm-question-boundary-v1/actual-sequence-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=False)
    rows = list(csv.DictReader((NATIVE/'actual-ppu-index.csv').open(newline='')))
    raw = (NATIVE/'actual-ppu.argb').read_bytes()
    size = 256*240*4
    assert len(raw) == size*len(rows) and len(rows) == 666
    indices = {int(q['ppu_frame']): i for i, q in enumerate(rows)}
    groups = [('impact', list(range(403, 419))), ('rise', list(range(422, 479, 8)))]
    selections = []
    for name, frames in groups:
        sheet = Image.new('RGB', (4*256, ((len(frames)+3)//4)*264), '#151923')
        draw = ImageDraw.Draw(sheet)
        for k, frame in enumerate(frames):
            i = indices[frame]
            data = raw[i*size:(i+1)*size]
            row = rows[i]
            assert row['mode'] == '0' and row['tier'] == '1'
            image = Image.frombytes('RGBA', (256, 240), data, 'raw', 'BGRA').convert('RGB')
            x, y = k%4*256, k//4*264
            draw.text((x+5, y+5), 'PPU '+str(frame)+' | update '+row['updates'], fill='white')
            sheet.paste(image, (x, y+24))
            selections.append(dict(group=name, row=row, ARGB_sha256=hashlib.sha256(data).hexdigest()))
        sheet.save(OUTPUT/(name+'.png'))
    proof = dict(offline_only=True, emulator_launches=0, pixel_edits=False,
        source_ARGB=str(NATIVE/'actual-ppu.argb'), source_ARGB_sha256=sha(NATIVE/'actual-ppu.argb'),
        source_index_sha256=sha(NATIVE/'actual-ppu-index.csv'),
        selections=selections, sheets={name: sha(OUTPUT/(name+'.png')) for name, _ in groups},
        limits='Actual completed-PPU samples selected by recorded PPU frame. Labels use recorded update snapshots and are not assumed to show that update publication. No sprite-height model or inferred OAM/palette bytes.',
        tool_sha256=sha(__file__))
    (OUTPUT/'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(samples=len(selections), output=str(OUTPUT))))


if __name__ == '__main__':
    main()
