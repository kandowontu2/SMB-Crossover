"""Pin LSR hurt body pixels from raw2.02 bitmap/mask matrices (no NES art)."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/reference'))
from prepare_crossover import frames


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'reference/crossover2'
    items = list(ET.parse(source/'main.xml').getroot().iter('item'))
    symbols = {}
    for tag in items:
        if tag.get('type') in ('SymbolClassTag', 'ExportAssetsTag') and tag.find('tags') is not None:
            symbols.update({n.text:i.text for i,n in zip(tag.find('tags'),tag.find('names'))})
    sprites = {i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
    specs = ((4,'Link','30',1,'244_com.smbc.graphics.skins.BmdInfo_Link000.png',
              (((138,217,1),1),((151,78,0),2),((255,160,68),3),((0,0,0),13))),
             (5,'Simon','80',17,'468_com.smbc.graphics.skins.BmdInfo_Simon000.png',
              (((82,33,0),1),((231,156,33),2),((247,214,165),3),((0,0,0),13))),
             (10,'Ryu','36',62,'550_com.smbc.graphics.skins.BmdInfo_Ryu000.png',
              (((146,144,255),1),((86,29,0),2),((255,196,234),3),((0,0,0),13),((255,255,255),10))))
    out = {}; provenance = {'swf_sha256':sha(source/'source.swf'), 'xml_sha256':sha(source/'main.xml'), 'characters':{}}
    for char,name,bitmap,number,image,colors in specs:
        timeline = frames(sprites[symbols[name]])
        if char==4:
            assert not any('walk' in f['labels'] for f in timeline)
            assert timeline[0]['labels']==['stand']
        frame = timeline[number-1]
        entries = sorted(frame['display'].items(),key=lambda p:int(p[0]))
        index,value = next((i,v) for i,(_,v) in enumerate(entries) if v.get('characterId')==bitmap)
        mask = next(v for _,v in entries[index+1:] if v.get('characterId')=='18')
        m,mm = value['matrix'],mask['matrix']
        x,y = (float(mm[k])/40 for k in ('translateX','translateY'))
        w,h = (float(mm[k])/2 for k in ('scaleX','scaleY'))
        left,top=x-float(m['translateX'])/40,y-float(m['translateY'])/40
        sheet=Image.open(source/'images'/image).convert('RGBA')
        pic=sheet.crop(tuple(round(v) for v in (left,top,left+w,top+h)))
        rows=[]
        for yy in range(pic.height):
            row=''
            for xx in range(pic.width):
                pixel=pic.getpixel((xx,yy))
                row += '.' if pixel[3]<128 or pixel[:3]==(111,49,152) else format(min(colors,key=lambda c:sum((pixel[i]-c[0][i])**2 for i in range(3)))[1],'x')
            rows.append(row)
        out[char]={'x':round(x),'y':round(y),'rows':rows}
        provenance['characters'][name]={'frame':number,'labels':frame['labels'],'sheet':image,'sheet_sha256':sha(source/'images'/image),'body_depth':entries[index][0],'body_matrix':m,'mask_matrix':mm,'colors':colors,'scope':'opaque primary body pixels; independent submovie shield/whip extras are not asserted here'}
    target=ROOT/'tests/fixtures/lsr-injury-body-source.lua'
    lua=['-- Raw2.02 primary body pixels only; no generated CHR/metasprite input.','return {']
    for char,p in out.items():
        lua.append('[%d]={x=%d,y=%d,rows={%s}},'%(char,p['x'],p['y'],','.join(json.dumps(s) for s in p['rows'])))
    lua.append('}')
    target.write_text('\n'.join(lua)+'\n')
    provenance['oracle_sha256']=sha(target)
    (ROOT/'tests/fixtures/lsr-injury-body-source.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print({c:(len(p['rows'][0]),len(p['rows']))for c,p in out.items()})


if __name__=='__main__':
    main()
