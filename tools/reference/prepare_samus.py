"""Export Samus from the same pinned hosted SWF used for Mega Man."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from prepare_crossover import ROOT, SOURCE_SHA256, SOURCE_URL, frames

def main():
    folder=ROOT/'reference/crossover'
    assert hashlib.sha256((folder/'super-mario-crossover.swf').read_bytes()).hexdigest()==SOURCE_SHA256
    tree=ET.parse(folder/'main.xml')
    sprites={x.get('spriteId'):x for x in tree.getroot().iter('item') if x.get('type')=='DefineSpriteTag'}
    ids=('1195','1239','1226','1704')
    manifests={sid:frames(sprites[sid]) for sid in ids}
    for sid in ids:
        tags=sprites[sid].find('subTags')
        hidden={x.get('depth') for x in tags if x.get('characterId') in ('658','660','1317')}
        for tag in list(tags):
            if tag.get('depth') in hidden:tags.remove(tag)
    tree.write(folder/'samus-graphics.xml',encoding='utf-8',xml_declaration=True)
    def ffdec(*args):
        subprocess.run(['java','-jar',str(ROOT/'.upstream/ffdec/ffdec.jar'),*map(str,args)],capture_output=True,text=True,check=True)
    ffdec('-xml2swf',folder/'samus-graphics.xml',folder/'samus-graphics.swf')
    for fmt in ('sprite','sprite:svg'):
        args=['-selectid',','.join(ids)]
        if fmt.endswith(':svg'):args+=['-format',fmt]
        ffdec(*args,'-export','sprite',folder/('samus-svg' if fmt.endswith(':svg') else 'samus-sprites'),folder/'samus-graphics.swf')
    for sid in ids:
        svg=next((folder/'samus-svg').glob(f'DefineSprite_{sid}_*/1.svg'))
        transform=list(ET.parse(svg).getroot())[0].get('transform')
        values=[float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',transform)]
        (folder/f'frames-{sid}.json').write_text(json.dumps({'origin':values[-2:],'frames':manifests[sid],
            'png_directory':str(next((folder/'samus-sprites').glob(f'DefineSprite_{sid}_*')).relative_to(ROOT))},indent=2)+'\n')
    scripts=folder/'decompiled/scripts/com/smbc'
    def constants(path):
        return {n:int(v) for n,v in re.findall(r'const\s+(\w+):(?:int|uint)\s*=\s*(\d+)',path.read_text())}
    facts={'source_url':SOURCE_URL,'sha256':SOURCE_SHA256,'fps':60,'nes_coordinate_scale':.5,
      'character':constants(scripts/'characters/Samus.as'),'shot':constants(scripts/'projectiles/SamusShot.as'),
      'bomb':constants(scripts/'projectiles/SamusBomb.as'),
      'physics':{'jump':500,'gravity':700,'water_gravity':400,'fall_cap':450,'release_friction':.0001,
        'walk_input_speed':180,'integrated_speed_cap':150,'water_ground_cap':90},
      'power_states':['short beam','long beam','wave beam'],
      'damage':{'beam':40,'bomb':100},'bomb_fuse_ms':950,'bomb_boost':230,
      'max_shots':3,'max_bombs':3}
    (ROOT/'docs/reference/samus.json').write_text(json.dumps(facts,indent=2)+'\n')
    print('Exported pinned Samus body, beams, bombs, death pieces and reference facts.')

if __name__=='__main__':main()
