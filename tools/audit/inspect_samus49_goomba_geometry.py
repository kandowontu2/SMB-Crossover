"""Independent, read-only geometry check for the recorded 1-2 contact."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root49k-samus-goomba-source-geometry-a.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    source = ROOT / 'reference/crossover2'
    assert sha(source / 'source.swf') == '6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    assert sha(source / 'main.xml') == '8edb72ebad459813b25303ce1f27d8df35e5a01192690d6e4d2ce23ce5e685df'
    sys.path.insert(0, str(ROOT / 'tools/reference'))
    from prepare_crossover import frames
    items = list(ET.parse(source / 'main.xml').getroot().iter('item'))
    symbols = {}
    for item in items:
        if item.get('type') in ('SymbolClassTag', 'ExportAssetsTag'):
            ids, names = item.find('tags'), item.find('names')
            if ids is not None and names is not None:
                symbols.update({n.text: i.text for i, n in zip(ids, names)})
    sprites = {i.get('spriteId'): i for i in items if i.get('type') == 'DefineSpriteTag'}
    assert symbols['Goomba'] == '134' and symbols['HRect'] == '14'
    primitive = sprites['14']
    placement = next(i for i in primitive.iter('item') if i.get('type') == 'PlaceObject2Tag')
    assert placement.get('characterId') == '13'
    shape = next(i for i in items if i.get('type') == 'DefineShapeTag' and i.get('shapeId') == '13')
    bounds = shape.find('shapeBounds').attrib
    assert [int(bounds[k]) for k in ('Xmin', 'Ymin', 'Xmax', 'Ymax')] == [0, 0, 160, 160]
    rects = []
    for frame in frames(sprites['134'])[:2]:
        matrix = next(v['matrix'] for v in frame['display'].values() if v.get('characterId') == '14')
        assert matrix['translateX'] == '-280' and matrix['translateY'] == '-600'
        assert abs(float(matrix['scaleX']) - 3.5) < .0001 and float(matrix['scaleY']) == 3.75
        rects.append(dict(frame=frame['frame'], labels=frame['labels'], matrix=matrix))
    receipt = ROOT / 'build/verification/agent49k-samus-early12-owner-review-d/report.json'
    actual = json.loads(receipt.read_text())
    assert actual['actual_fractional_fields']['MmXFractionQ16'] == 49152
    assert actual['actor']['world_x'] == 1177 and actual['actor']['id'] == 6
    # This is an explicit alignment assumption, not a claim that source enemy
    # integration and native collision order have been proven frame-identical.
    player_x = 1165 + 49152 / 65536
    source_player_right = player_x + 14.75
    enemy_left_range = [1177 + 8 - 7, 1177 + 8 - 7 + 1]
    assert source_player_right > enemy_left_range[1]
    refs = [source / 'source.json', source / 'source.swf', source / 'main.xml',
            source / 'extracted/scripts/com/smbc/enemies/Goomba.as',
            ROOT / 'src/common.s', receipt]
    data = dict(status='READ_ONLY_SOURCE_GEOMETRY_WITH_EXPLICIT_ALIGNMENT_QUALIFICATION',
                references={str(p.relative_to(ROOT)): sha(p) for p in refs},
                source_walk_HRects=rects, primitive_shape_bounds_twips=bounds,
                source_nominal_local_NES_rectangle=[-7, -15, 7, 0],
                source_matrix_X_rounding_less_than_NES_pixels=.001,
                alignment_assumption='Source Goomba feet-center at native sprite-left X+8, with native fractional position in [0,1). Full native/source animation and collision phase is not claimed.',
                actual_player_X_fraction=.75, conditional_source_player_right=source_player_right,
                conditional_source_Goomba_left_range=enemy_left_range,
                conditional_overlap_minimum_NES_pixels=source_player_right-enemy_left_range[1],
                inference='Under this explicit anchor alignment the recorded contact persists with fractional source widths. Shrinking native player right by .25 while omitting actual .75 fraction is not a valid false-positive demonstration.',
                native_calls=0, CPU_model_calls=0, runtime_changes=0)
    OUT.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)), sha256=sha(OUT), status=data['status'], conditional_overlap_minimum=data['conditional_overlap_minimum_NES_pixels'])))


if __name__ == '__main__':
    main()
