"""Extract the exact linked Crossover SWF as a read-only porting reference."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = 'https://www.smbgames.be/roms/super-mario-crossover.swf'
SOURCE_SHA256 = '46bdcf0b60721bbe0f006cdb083f503e0312feacede6f65f2942f7a5a406b1eb'


def frames(sprite):
    result = []
    display = {}
    labels = []
    for tag in sprite.find('subTags'):
        kind = tag.get('type', '')
        if kind == 'FrameLabelTag':
            labels.append(tag.get('name'))
        elif kind.startswith('PlaceObject'):
            state = display.setdefault(tag.get('depth'), {})
            state.update(tag.attrib)
            matrix = tag.find('matrix')
            if matrix is not None:
                state['matrix'] = dict(matrix.attrib)
        elif kind == 'RemoveObject2Tag':
            display.pop(tag.get('depth'), None)
        elif kind == 'ShowFrameTag':
            result.append({'frame': len(result)+1, 'labels': labels,
                           'display': json.loads(json.dumps(display))})
            labels = []
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--swf', type=Path, default=ROOT/'reference/crossover/super-mario-crossover.swf')
    parser.add_argument('--ffdec', type=Path, default=ROOT/'.upstream/ffdec/ffdec.jar')
    args = parser.parse_args()
    if hashlib.sha256(args.swf.read_bytes()).hexdigest() != SOURCE_SHA256:
        parser.error('The SWF does not match the linked build; audit the version before importing.')
    folder = ROOT/'reference/crossover'

    def ffdec(*arguments):
        result = subprocess.run(['java', '-jar', str(args.ffdec), *map(str, arguments)],
                                capture_output=True, text=True, check=True)

    ffdec('-export', 'script', folder/'decompiled', args.swf)
    ffdec('-export', 'binaryData,sound', folder/'assets', args.swf)
    embedded = next((folder/'assets').glob('*MainSwfClassContainer_MainSwfClass_dataClass.bin'))
    ffdec('-swf2xml', embedded, folder/'main.xml')
    tree = ET.parse(folder/'main.xml')
    root = tree.getroot()
    sprites = {item.get('spriteId'): item for item in root.iter('item')
               if item.get('type') == 'DefineSpriteTag'}
    manifest = {key: frames(sprites[key]) for key in ('73', '691', '1270', '1643', '1673')}
    # Red rectangles are debugging hitboxes hidden by ActionScript at runtime.
    # Remove them only in an asset-export copy. Export the head separately so
    # its real power-state/action frame can be composed, rather than frame 1.
    for key in ('691', '1270', '1673'):
        tags = sprites[key].find('subTags')
        hidden = {tag.get('depth') for tag in tags
                  if tag.get('characterId') in ('658', '660', '1317') or
                  (key == '691' and tag.get('characterId') == '73')}
        for tag in list(tags):
            if tag.get('depth') in hidden:
                tags.remove(tag)
    tree.write(folder/'graphics-only.xml', encoding='utf-8', xml_declaration=True)
    ffdec('-xml2swf', folder/'graphics-only.xml', folder/'graphics-only.swf')
    ffdec('-selectid', '73,691,1270,1643,1673', '-export', 'sprite', folder/'clean-sprites', folder/'graphics-only.swf')
    ffdec('-selectid', '73,691,1270,1643,1673', '-format', 'sprite:svg', '-export', 'sprite', folder/'clean-svg', folder/'graphics-only.swf')
    for key in manifest:
        svg = next((folder/'clean-svg').glob(f'DefineSprite_{key}_*/1.svg'))
        svg_root = ET.parse(svg).getroot()
        transform = list(svg_root)[0].get('transform')
        values = [float(value) for value in re.findall(r'-?\d+(?:\.\d+)?', transform)]
        (folder/f'frames-{key}.json').write_text(json.dumps({
            'origin': values[-2:], 'frames': manifest[key],
            'png_directory': str(next((folder/'clean-sprites').glob(f'DefineSprite_{key}_*')).relative_to(ROOT)),
        }, indent=2)+'\n')
    scripts = folder/'decompiled/scripts/com/smbc'
    character = (scripts/'characters/MegaMan.as').read_text()
    bullet = (scripts/'projectiles/MegaManBullet.as').read_text()

    def constants(text):
        return {name: int(value) for name, value in re.findall(
            r'const\s+(\w+):(?:int|uint)\s*=\s*(\d+)', text)}

    facts = {
        'source_url': SOURCE_URL, 'sha256': SOURCE_SHA256,
        'stage': {'width': 512, 'height': 480, 'fps': 60, 'nes_coordinate_scale': 0.5},
        'movement': {'acceleration': 600, 'friction_x': 1e-7, 'friction_y': 1e-6,
                     'max_speed_x': 150, 'min_speed_x': 5, 'jump_speed': 580,
                     'gravity': 1100, 'max_fall_speed': 700,
                     'water_gravity': 500, 'water_jump_speed': 550,
                     'water_ground_speed_cap': 90, 'water_fall_speed_cap': 250},
        'character_constants': constants(character),
        'projectile_constants': constants(bullet), 'projectile_speed': 430,
        'damage': constants((scripts/'data/DamageValue.as').read_text()),
        'health': constants((scripts/'data/HealthValue.as').read_text()),
        'charge_release_thresholds_ms': {'weak': 800, 'full': 1450},
        'power_states': ['helmetless', 'helmet and charge', 'fire shots and stronger full charge'],
        'bullet_limit': {'normal': 3, 'normal_blocked_while_full_charge_active': True},
        'music_reference': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (folder/'assets/sounds').glob('*MegaMan*')},
    }
    output = ROOT/'docs/reference/crossover.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(facts, indent=2)+'\n')
    print('Prepared pinned source, original graphics, audio, frame origins and behavior facts.')


if __name__ == '__main__':
    main()
