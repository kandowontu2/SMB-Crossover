"""Freeze suitless crouch silhouettes directly from the pinned skin cells.

This deliberately does not import the production extractor or CHR packer.
The original SWF31/32 mask/matrix maps the48x64 native pose canvas to
sheet(x+101,y+6) / sheet(x+151,y+6), clipped vertically to1..49.
"""
from pathlib import Path
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
source=next((ROOT/'reference/crossover2/images').glob('*_Samus003.png'))
image=Image.open(source).convert('RGBA')
lines=['-- Independent source skin003 cells, not generated NES tiles.','return {']
for name,left in [('CROUCH',101),('CROUCHSHOOT',151)]:
    lines.append(f' ["{name}"]={{')
    for y in range(64):
        row=''
        for x in range(48):
            p=image.getpixel((x+left,y+6))
            row+='1' if 1<=y<50 and p[3] and p[:3]!=(111,49,152) else '0'
        lines.append(f'  "{row}",')
    lines.append(' },')
lines.append('}')
(ROOT/'tests/samus-suitless-crouch-source.lua').write_text('\n'.join(lines)+'\n')
(ROOT/'build/samus-crouch-source-provenance.json').write_text(json.dumps({
    'source':str(source.relative_to(ROOT)),
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'native_sheet_offsets':{'CROUCH':[101,6],'CROUCHSHOOT':[151,6]},
    'source_timeline_frames':[31,32],
    'source_xml_sha256':hashlib.sha256((ROOT/'reference/crossover2/main.xml').read_bytes()).hexdigest(),
},indent=2)+'\n')
print('Frozen independent Samus suitless crouch/shoot source cells.')
