"""Extract Bill, Link and Simon from the pinned hosted Crossover build."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from prepare_crossover import ROOT, SOURCE_SHA256, SOURCE_URL, frames

IDS=('1194','1152','1141','1131','690','726','1290','1283','1535','1542','1551')

def main():
    folder=ROOT/'reference/crossover'
    assert hashlib.sha256((folder/'super-mario-crossover.swf').read_bytes()).hexdigest()==SOURCE_SHA256
    tree=ET.parse(folder/'main.xml')
    sprites={x.get('spriteId'):x for x in tree.getroot().iter('item') if x.get('type')=='DefineSpriteTag'}
    manifests={sid:frames(sprites[sid]) for sid in IDS}
    for sprite in sprites.values():
        tags=sprite.find('subTags')
        hidden={x.get('depth') for x in tags if x.get('characterId') in ('658','660','1317')}
        if sprite.get('spriteId')=='1194':
            # Bill hides these three persistent children outside "main";
            # compose his independently animated torso/legs at runtime poses.
            hidden.update(('4','6','8'))
        for tag in list(tags):
            if tag.get('depth') in hidden:tags.remove(tag)
    tree.write(folder/'roster-graphics.xml',encoding='utf-8',xml_declaration=True)
    def ffdec(*args):
        subprocess.run(['java','-jar',str(ROOT/'.upstream/ffdec/ffdec.jar'),*map(str,args)],capture_output=True,text=True,check=True)
    ffdec('-xml2swf',folder/'roster-graphics.xml',folder/'roster-graphics.swf')
    for fmt in ('sprite','sprite:svg'):
        args=['-selectid',','.join(IDS)]
        if fmt.endswith(':svg'):args+=['-format',fmt]
        ffdec(*args,'-export','sprite',folder/('roster-svg' if fmt.endswith(':svg') else 'roster-sprites'),folder/'roster-graphics.swf')
    for sid in IDS:
        svg=next((folder/'roster-svg').glob(f'DefineSprite_{sid}*/1.svg'))
        transform=list(ET.parse(svg).getroot())[0].get('transform')
        values=[float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',transform)]
        (folder/f'frames-{sid}.json').write_text(json.dumps({'origin':values[-2:],'frames':manifests[sid],
            'png_directory':str(next((folder/'roster-sprites').glob(f'DefineSprite_{sid}*')).relative_to(ROOT))},indent=2)+'\n')
    scripts=folder/'decompiled/scripts/com/smbc'
    def constants(path):
        return {n:float(v) for n,v in re.findall(r'const\s+(\w+):(?:int|uint|Number)\s*=\s*([\d.]+)',path.read_text())}
    facts={'source_url':SOURCE_URL,'sha256':SOURCE_SHA256,'fps':60,'nes_coordinate_scale':.5,
      'characters':{name:constants(scripts/f'characters/{name}.as') for name in ('Bill','Link','Simon')},
      'damage':constants(scripts/'data/DamageValue.as')}
    (ROOT/'docs/reference/roster.json').write_text(json.dumps(facts,indent=2)+'\n')
    print('Exported pinned Bill, Link and Simon body/weapon frames and reference facts.')

if __name__=='__main__':main()
