"""Archive exact 2.02 injury effect pixels without reading generated NES art."""
from pathlib import Path
import hashlib, json, re, sys, xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/reference'))
from prepare_crossover import frames
from build_special_art import extract

def main():
    source = ROOT / 'reference/crossover2'
    provenance = json.loads((source / 'source.json').read_text())
    assert hashlib.sha256((source / 'source.swf').read_bytes()).hexdigest() == provenance['sha256']
    items = list(ET.parse(source / 'main.xml').getroot().iter('item'))
    symbols = {}
    for tag in items:
        if tag.get('type') in ('SymbolClassTag', 'ExportAssetsTag'):
            ids, names = tag.find('tags'), tag.find('names')
            if ids is not None and names is not None:
                symbols.update({n.text: i.text for i, n in zip(ids, names)})
    sprites = {i.get('spriteId'): i for i in items if i.get('type') == 'DefineSpriteTag'}
    timeline = frames(sprites[symbols['MegaManSimpleGraphics']])
    labels = {label: f['frame'] for f in timeline for label in f['labels']}
    selected = [labels['damageSplash']] + list(range(labels['damageSparkStart'], labels['damageSparkEnd'] + 1))
    records, images = {}, {}
    for char, name in (('megaman', '625_com.smbc.graphics.skins.BmdInfo_MegaMan000.png'),
                       ('bass', '412_com.smbc.graphics.skins.BmdInfo_Bass000.png')):
        path = source / 'images' / name
        images[char] = dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        pictures = extract(timeline, 24, Image.open(path).convert('RGBA'))
        result = []
        for n in selected:
            im = pictures[n - 1]
            x0, y0, x1, y1 = im.getbbox()
            palette = sorted({im.getpixel((x, y))[:3] for y in range(y0, y1) for x in range(x0, x1) if im.getpixel((x, y))[3] >= 128})
            result.append(dict(frame=n, labels=timeline[n - 1]['labels'], x=x0-48, y=y0-48,
                colors=['%02x%02x%02x' % p for p in palette],
                rows=[''.join('.' if im.getpixel((x, y))[3] < 128 else str(palette.index(im.getpixel((x, y))[:3]))
                              for x in range(x0, x1)) for y in range(y0, y1)]))
        records[char] = result
    script = source / 'extracted/scripts/com/smbc/characters/base/MegaManBase.as'
    code = script.read_text()
    constants = {k: int(re.search(r'const\s+'+k+r':int\s*=\s*(\d+)', code)[1])
                 for k in ('FLICKER_TMR_DEL', 'NO_DAMAGE_TMR_DEL', 'TAKE_DAMAGE_TMR_DEL', 'TAKE_DAMAGE_SPEED')}
    body=frames(sprites[symbols['MegaMan']])
    hurt=next(f for f in body if 'takeDamage' in f['labels'])
    mask=next(v for v in hurt['display'].values()if v.get('characterId')=='18')['matrix']
    rect=next(v for v in hurt['display'].values()if v.get('characterId')==symbols['HRect'])['matrix']
    assert round(float(mask['scaleY']))==70 and int(rect['translateY'])==-960
    geometry=dict(frame=hurt['frame'],body_mask=mask,hurt_rect=rect,display_height_flash=round(float(mask['scaleY'])),hurt_height_flash=48)
    data = dict(swf_sha256=provenance['sha256'], source_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                source_constants=constants, source_images=images, timeline_labels=labels, effect_pixels=records,geometry=geometry)
    target = ROOT / 'tests/fixtures/megaman-bass-injury-source-art.json'
    target.write_text(json.dumps(data, indent=2)+'\n')
    lua=['-- Independent raw2.02 mask pixels and body geometry, not generated NES art.',
         'return {displayHeight=35,hurtHeight=24,pictures={']
    for i,p in enumerate(records['megaman']):
        lua.append('[%d]={x=%d,y=%d,rows={%s}},'%(i,p['x'],p['y'],','.join(json.dumps(s)for s in p['rows'])))
    lua.append('}}')
    (ROOT/'tests/fixtures/megaman-bass-injury-source-pixels.lua').write_text('\n'.join(lua)+'\n')
    print(json.dumps(dict(path=target.relative_to(ROOT).as_posix(), frames=selected,
                          labels=labels, constants=constants, bytes=target.stat().st_size)))

if __name__ == '__main__':
    main()
