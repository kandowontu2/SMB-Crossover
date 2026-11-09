"""Extract exact GBC Mini fireball silhouettes and source cadence, without ROM output."""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

from PIL import Image

from prepare_mini_mario_art_1103_v12 import GB, GBPIN, R, decode, encode, index, sha


DONOR = 'Mico27/SuperMarioBrosMini'
DONOR_TREE = '56d5a30ff8f58096c074ca59656efc5f787d0edb'
COMPILER = 'chrismaltby/gb-studio'
COMPILER_TREE = '49563d9ab3e8d78e10b0fc7b0797f23676d3045f'
DIRECT = {
    'assets/sprites/effects.png': '601549257d904caff9cea9c3035de2431ee610b8',
    'assets/sprites/effects.png.gbsres': 'ce02959e29d12fd6151361c2c2a881f3bee2b7ee',
    'project/scenes/1-1/actors/fireball_1.gbsres': '8dad78cef82534eac3f7cd79aba3ef83a4a4cf80',
    'project/palettes/overworld_sp_2.gbsres': '11e961d8802846e37861c73d2ceec7314276ec7e',
}
TOOLS = {
    'src/lib/compiler/applyPrefabs.ts': '560c8dbc431e2617cd0f12dbd67fc08ee784560e',
    'src/lib/compiler/generateGBVMData.ts': '10e277eb9b95740d56db17cec80dff8bc3c97170',
}
ATTACK = R/'build/mini-fireball-contract-1103/original-inputs.zip'
REFERENCE = R/'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1/reference.zip'
COMPILER_REFERENCE = R/'build/mini-mario-art-1103-v12/compiler-inputs.zip'
ATTR_SOURCE = R/'build/mini-native-lifts-v2-1108/mini-lift.s'
ATTR_ROM = ATTR_SOURCE.with_name('candidate.nes')
ATTR_PARENT = 'ffdb314bcf94c8608c4fc75758a53953a9f1f0f30df5256d4feb6e9ac327ca93'


def git_blob(data):
    return hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()


def fetch(entry):
    repo, name, pin = entry
    response = json.loads(subprocess.check_output(['gh', 'api', f'repos/{repo}/git/blobs/{pin}']))
    data = base64.b64decode(response['content'])
    assert response['encoding'] == 'base64' and response['size'] == len(data) and git_blob(data) == pin
    return name, data


def source_art(gb, sources):
    sprite = json.loads(sources['assets/sprites/effects.png.gbsres'])
    sheet = Image.open(io.BytesIO(sources['assets/sprites/effects.png'])).convert('RGB')
    assert sheet.size == (120, 16) and sprite['id'] == '8dbb443a-eb83-48bb-86c9-ffd9012f45c7'
    states = {state['name']: state for state in sprite['states']}
    assert all(states[name]['animationType'] == 'fixed' for name in ('Fireball', 'FireballHit'))
    # GB Studio's Fixed animation type maps all directional entries to editor index0.
    keys = ('sliceX', 'sliceY', 'x', 'y', 'flipX', 'flipY', 'paletteIndex', 'objPalette', 'priority')
    moving, impact = [
        [[tuple(tile[k] for k in keys) for tile in frame['tiles']]
         for frame in states[name]['animations'][0]['frames']]
        for name in ('Fireball', 'FireballHit')
    ]
    assert moving == [[(slice_x, 0, 0, 0 if flipped else 8, flipped, flipped, 2, 'OBP0', False)]
                      for flipped in (False, True) for slice_x in (72, 80)]
    assert impact == [[(slice_x, 0, 0, 8, False, False, 2, 'OBP0', False)] for slice_x in (88, 96, 88)] + [[]]
    # Native palette2's physical $16, $30, $27 are red, white, orange.
    gbc_to_nes = (0, 2, 3, 1)
    frames = {}
    packed = bytearray()
    for i, (name, slice_x) in enumerate(zip('ABCD', range(72, 104, 8))):
        px = [index(sheet.getpixel((x, y))) for y in range(16) for x in range(slice_x, slice_x+8)]
        assert not any(px[:64]) and any(px[64:])
        gb_pair = encode(px, interleaved=True)
        gb_at = 0x10ff20+32*i
        assert gb[gb_at:gb_at+32] == gb_pair and gb.count(gb_pair[16:]) == 1
        nes_px = [gbc_to_nes[color] for color in px[64:]] + [0]*64
        nes_pair = encode(nes_px)
        assert decode(nes_pair) == nes_px
        opaque = [(p%8, p//8) for p, color in enumerate(nes_px) if color]
        bounds = [min(v[0] for v in opaque), min(v[1] for v in opaque),
                  max(v[0] for v in opaque)+1, max(v[1] for v in opaque)+1]
        frames[name] = dict(source_slice_x=slice_x, GB_pair_offset=gb_at, GB_interleaved_pair=gb_pair.hex(),
                            NES_pair=nes_pair.hex(), opaque_pixels=len(opaque), opaque_bounds_half_open=bounds,
                            source_opaque_rows=[''.join(map(str, px[64+y*8:72+y*8])) for y in range(8)])
        packed.extend(nes_pair)
    assert [frames[name]['opaque_pixels'] for name in 'ABCD'] == [23, 23, 8, 44]
    records = ('f800100280', 'f800120280', '0000106280', '0000126280', 'f800140280', 'f800160280', '80')
    offsets = list(range(0xe39e7, 0xe3a18, 8))
    assert len(offsets) == len(records)
    for at, record in zip(offsets, records):
        assert gb[at:at+len(bytes.fromhex(record))].hex() == record
    targets = offsets[:4] + [offsets[4], offsets[5], offsets[4], offsets[6]]
    assert gb[0xe3da3:0xe3db3] == b''.join((0x4000|(at&0x3fff)).to_bytes(2, 'little') for at in targets)
    bounds = [sprite[k] for k in ('boundsX', 'boundsY', 'boundsWidth', 'boundsHeight')]
    assert bounds == [0, 8, 8, 8]
    return bytes(packed), frames, dict(records=dict(zip(map(hex, offsets), records)),
                                       pointers_start=0xe3da3, targets=targets, resource_bounds_XYWH=bounds)


def cadence_palette(sources):
    with ZipFile(ATTACK) as z:
        prefab = z.read('project/prefabs/actors/fireball.gbsres')
        scene = z.read('project/scenes/1-1/scene.gbsres')
        attack = z.read('project/scripts/onattack.gbsres')
    with ZipFile(REFERENCE) as z:
        engine = z.read('plugins/GameSpecific/engine/src/core/actor.c')
    with ZipFile(COMPILER_REFERENCE) as z:
        palette_compiler = z.read('src/lib/compiler/compileData.ts')
        fixed_mapping = z.read('src/shared/lib/sprites/helpers.ts')
    assert git_blob(prefab) == '35ababa5c48c537883b26246252eb33afa137064'
    assert git_blob(scene) == '298beee054297e0c02f182dd8e074f9686d794f9'
    assert git_blob(attack) == 'df3d99547a436a858ae1817f639f83a24b51045c'
    assert b'EVENT_ACTOR_SET_DIRECTION' not in attack
    actor = json.loads(sources['project/scenes/1-1/actors/fireball_1.gbsres'])
    meta = json.loads(prefab)
    assert actor['prefabId'] == meta['id'] and actor['animSpeed'] == 15 and meta['animSpeed'] == 3
    assert actor['direction'] == 'down' and meta['frame'] == 0
    assert actor['prefabScriptOverrides'] == {}
    assert b'...actor,\n          ...mapActorScript(prefab, applyScriptEventOverrides)' in sources['src/lib/compiler/applyPrefabs.ts']
    assert b'anim_tick: actor.animSpeed' in sources['src/lib/compiler/generateGBVMData.ts']
    assert b'(game_time & actor->anim_tick) == 0' in engine
    assert b'actor->frame++;' in engine and b'actor->frame = actor->frame_start;' in engine
    assert b'actor_set_anim_idle(actor);' in engine and b'(actor->frame_start != frame_start)' in engine
    assert b'const fixedIndexes = [0]' in fixed_mapping
    first = meta['startScript'][0]['args']
    assert first['spriteStateId'] == 'Fireball' and first['loopAnim'] is True
    hit, = [event['args'] for event in meta['hit1Script'] if event['command'] == 'EVENT_LOAD_PROJECTILE_SLOT']
    assert (hit['spriteStateId'], hit['animSpeed'], hit['loopAnim'], hit['lifeTime']) == ('FireballHit', 3, False, 0.1)
    palette = json.loads(sources['project/palettes/overworld_sp_2.gbsres'])
    assert json.loads(scene)['spritePaletteIds'][2] == palette['id']
    assert b'colors: [p.colors[0], p.colors[0], p.colors[1], p.colors[3]]' in palette_compiler
    assert palette['colors'] == ['ffffff', 'fead00', '000000', 'cd4210']
    return dict(animation=dict(mask=3, tick='While active and traversed by renderer, (game_time & 3) == 0 advances '
                                    'this actor before draw. Hold each phase for four source game updates in steady rendering.',
                               activation='Initial phase0. Deactivate retains frame; activation selects the same fixed range. '
                                          'Source resets frame only if the animation range changes.',
                               moving=['A', 'B', 'A flip-X+Y', 'B flip-X+Y'], impact=['C', 'D', 'C', 'blank'],
                               impact_loop=False, impact_source_life_seconds=0.1,
                               facing='The source uses the same fixed animation in all directions. Attack writes velocity, not direction.'),
                palette=dict(scene='1-1', OAM_CGB_palette=2, source_name=palette['name'],
                             resource_RGB=palette['colors'], GBC_opaque_RGB=['ffffff', 'fead00', 'cd4210'],
                             native_NES_OAM_palette=2, existing_NES_indices=[0x16, 0x30, 0x27],
                             donor_index_to_NES_index=[0, 2, 3, 1],
                             adaptation='Preserve installed red/white/orange NES palette; map source indexed pixels to those entries.'))


def packing_evidence():
    raw = ATTR_ROM.read_bytes()
    source = ATTR_SOURCE.read_text()
    assert sha(raw) == ATTR_PARENT
    start = 1048592+967*1024
    kernel = raw[1048592+962*1024:start]
    attrs = raw[start+0x300:start+0x400]
    assert len(attrs) == 256 and max(i for i, value in enumerate(attrs) if value) == 0xc5
    assert source.count('lda MiniTileAttributes,x') == 2
    sites = [i for i in range(len(kernel)-3) if kernel[i:i+3] == bytes.fromhex('bd00d3')]
    assert len(sites) == 2
    assert kernel[sites[0]+3:sites[0]+5] == bytes.fromhex('4a4a')
    assert kernel[sites[1]+3:sites[1]+7] == bytes.fromhex('2903c901')
    return dict(parent_SHA256=ATTR_PARENT, metadata_page=967, encoded_attrs_SHA256=sha(attrs),
                last_nonzero_attr=0xc5, unused_value_tail_half_open=[0xc6, 0x100],
                direct_readers=[hex(0xa000+i) for i in sites],
                proposed_pair_offsets={'A': 'D2E0', 'B': 'D3E0', 'C': 'D3A0', 'D': 'D3C0'},
                note='Root proposes reconstructing the original 256-entry RAM table at cold load. '
                     'The nonzero ROM attr preimages at C/D must therefore be moved or regenerated during cold load. '
                     'Do not treat the current ROM table tail as free until that reconstruction is proven.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True)
    inputs = [(repo, name, pin) for repo, paths in ((DONOR, DIRECT), (COMPILER, TOOLS)) for name, pin in paths.items()]
    with ThreadPoolExecutor(max_workers=3) as pool:
        sources = dict(pool.map(fetch, inputs))
    gb = GB.read_bytes()
    assert len(gb) == 2097152 and sha(gb) == GBPIN
    packed, frames, evidence = source_art(gb, sources)
    mechanics = cadence_palette(sources)
    result = dict(passed=True, source_only=True, ROM_written=False, native_emulator_run=False,
                  donor_tree=DONOR_TREE, GBC_SHA256=GBPIN, compiler_tree=COMPILER_TREE,
                  source_files={name: dict(git_blob=git_blob(data), SHA256=sha(data), size=len(data))
                                for name, data in sources.items()},
                  cached_source_bindings={p.relative_to(R).as_posix(): sha(p.read_bytes())
                                          for p in (ATTACK, REFERENCE, COMPILER_REFERENCE, ATTR_SOURCE)},
                  bitmap_order='ABCD, each 32 NES bytes. Normal opaque half first, blank second.',
                  packed_SHA256=sha(packed), frames=frames, donor_pose_stream=evidence,
                  NES_plan=dict(normal_OAM_Y_from_native=1, flipped_OAM_Y_from_native=-7,
                                OAM_X_from_native=4, normal_attrs=2, flipped_attrs=0xc2,
                                moving_native_opaque_half_open_XYXY=[5, 3, 11, 9],
                                preserve_two_native_slots_and_4x4_gameplay_collision=True,
                                interpretation='Center the source art on the existing native fireball anchor. '
                                               'Keep impact event and lifetime bound to the host actor lifecycle.'),
                  packing=packing_evidence(), **mechanics)
    (args.output/'mini-fireball-authentic.chr').write_bytes(packed)
    (args.output/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, art_bytes=len(packed), SHA256=sha(packed),
                          donor_pose_stream=evidence, palette=mechanics['palette']['GBC_opaque_RGB'])))


if __name__ == '__main__':
    main()
