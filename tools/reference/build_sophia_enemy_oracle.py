"""Pin uncompressed source enemy-explosion pixels before native art packing."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
from PIL import Image
from build_remaining_art import extract
from prepare_crossover import frames
ROOT=Path(__file__).resolve().parents[2]
items=list(ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item'))
symbols={}
for t in items:
    if t.get('type') in ('SymbolClassTag','ExportAssetsTag'):
        ids,names=t.find('tags'),t.find('names')
        if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
sprite=next(i for i in items if i.get('type')=='DefineSpriteTag' and i.get('spriteId')==symbols['SophiaExplosion'])
path=next((ROOT/'reference/crossover2/images').glob('*_Sophia000.png'))
pictures=extract(frames(sprite),44,Image.open(path).convert('RGBA'))
lines=['-- Frozen source SWF masks/matrices; no NES CHR or metasprite data read.','-- Six enemy-death frames; source frame9 is intentionally blank.','return {']
colors=[(228,0,88),(255,255,255),(0,0,0)]
for index in range(8,14):
    pic=pictures[index-1];bbox=pic.getbbox()
    if not bbox:
        lines.append(f' [{index-7}]={{width=0,height=0,pixels={{}}}},');continue
    pic=pic.crop(bbox)
    pixels=[255 if v[3]<128 else 17+min(range(3),key=lambda c:sum((v[k]-colors[c][k])**2 for k in range(3)))for v in pic.getdata()]
    lines.append(f' [{index-7}]={{width={pic.width},height={pic.height},pixels={{{",".join(map(str,pixels))}}}}},')
lines.append('}')
target=ROOT/'tests/fixtures/sophia-enemy-pixels.lua';target.write_text('\n'.join(lines)+'\n')
target.with_suffix('.json').write_text(json.dumps({'source_sheet_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_swf_sha256':hashlib.sha256((ROOT/'reference/crossover2/source.swf').read_bytes()).hexdigest(),'frames':list(range(8,14)),'oracle_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'comparison':'Cropped source SWF shape and native palette indices before CHR packing; blank9 required'},indent=2)+'\n')
