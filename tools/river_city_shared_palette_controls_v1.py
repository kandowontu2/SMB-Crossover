"""Authenticated RCR art through the genuine host renderer, independently linked.

The private data-only link does not replace the frozen cartridge or claim that
RcSetPose, the shared menu, palette compositor or native gameplay is integrated.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address
from prepare_river_city_reference import NATIVE, native_pixels
from prepare_river_city_assets import POSES, decode


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = R/'build/river-city-shared-palette-controls-v1'
    out.mkdir(exist_ok=False)
    rom = R/'build/roster-expansion-mac-pipe-corner-v3.nes'
    assert sha(rom) == '33d2c7a7bf58aa040f2911d44f1d59dddb4c9b40b3e8727334cf46db74915f97'
    atlas = R/'chr/characters/river-city-shared-palette.chr'
    metadata = R/'chr/characters/river-city-shared-palette-v3.json'
    records = json.loads(metadata.read_text())
    unit = out/'art.s'
    unit.write_text('.include "river_city_shared_palette_art.inc"\n')
    cfg = out/'art.cfg'
    cfg.write_text('MEMORY { ART: start=$cb80,size=$1000,file=%O,fill=yes,fillval=$ff; }\n'
                   'SEGMENTS { RIVER_CITY_ART: load=ART,type=ro; }\n')
    obj, binary, labels = [out/x for x in ('art.o', 'art.bin', 'art.lbl')]
    commands = [
        [str(R/'tools/Windows/cc65/bin/ca65.exe'), '--cpu', '6502x', '-g',
         '-I', str(R/'src'), '-o', str(obj), str(unit)],
        [str(R/'tools/Windows/cc65/bin/ld65.exe'), '-C', str(cfg), '-Ln', str(labels),
         '--dbgfile', str(out/'art.dbg'), '-o', str(binary), str(obj)]]
    for i, command in enumerate(commands):
        result = subprocess.run(command, cwd=R, capture_output=True, text=True)
        (out/f'link-{i}.log').write_text(result.stdout+result.stderr)
        assert result.returncode == 0, result.stderr
    # Debug symbols include local ART labels without exporting a fake host API.
    symbols = {}
    for line in (out/'art.dbg').read_text().splitlines():
        if not line.startswith('sym\t'):
            continue
        d = dict(x.split('=', 1) for x in line.split('\t', 1)[1].split(',') if '=' in x)
        if 'val' in d:
            symbols[d['name'].strip('"')] = int(d['val'], 0)
    bundle = scoped_load(rom)
    raw = bytearray(bundle['raw'])
    start = 16+70*8192+(0xcb80 & 8191)
    raw[start:start+4096] = binary.read_bytes()
    bundle['raw'] = bytes(raw)
    source = NATIVE.read_bytes()
    assert sha(NATIVE) == '276c1a1a37685717c0d808490100874a949ea79b68bdef0fcaeeab4586a72f62'
    pages = records['physical_pages']
    page_bytes = {page: atlas.read_bytes()[i*1024:(i+1)*1024] for i, page in enumerate(pages)}
    rows, capacity = [], []
    for variant in (0, 1):
        for face in (1, 2):
            for pose, (name, native_pose) in enumerate(POSES):
                original, _, _ = native_pixels(source, native_pose, variant, face)
                combined = {}
                for ink in (0, 1):
                    suffix = 'R' if face == 1 else 'L'
                    label = f'RcV{variant}{"Ink" if ink else "Body"}{pose}{suffix}'
                    ptr = symbols[label]
                    q = Arena(bundle, 21)
                    q.m.page(2, 70)
                    q.put(CurrentOAMOffset=0, R0=ptr & 255, R1=ptr >> 8,
                          R3=0, R4=96, R5=0, R6=96, R7=1, GuestOamRotationActive=0)
                    c, _ = q.invoke('MetaspriteRenderLoop')
                    assert c.p & 1
                    count = q.get('CurrentOAMOffset')//4
                    record = next(a for a in records['records'] if a['variant'] == variant
                                  and a['face'] == face and a['pose'] == pose and a['ink'] == bool(ink))
                    assert count == len(record['parts'])
                    pixels = {}
                    for part in range(count-1, -1, -1):
                        xx, yy = q.get('Sprite_X_Position', part*4)-96, q.get('Sprite_Y_Position', part*4)-96
                        tt, aa = q.get('Sprite_Tilenumber', part*4), q.get('Sprite_Attributes', part*4)
                        assert aa & 3 == (3 if ink else 0)
                        tile = (tt-64 if ink else tt)*16
                        pattern = decode(page_bytes[record['page']][tile:tile+32])
                        for y in range(16):
                            for x in range(8):
                                v = pattern[y][7-x if aa & 64 else x]
                                if v:
                                    pixels[xx+x, yy+y] = 1 if ink else {1:3, 2:2, 3:4}[v]
                    expected = {p:v for p,v in original.items() if (v == 1) == bool(ink)}
                    assert pixels == expected, (variant, face, pose, ink)
                    assert not (combined.keys() & pixels.keys())
                    combined.update(pixels)
                    length = count*4
                    for offset, rotation in ((0,0), (128,0), (224,0), (252,0), (240,28), (0,252)):
                        q.put(CurrentOAMOffset=offset, GuestOamRotationActive=int(rotation != 0),
                              RgOamRotation=rotation, R0=ptr & 255, R1=ptr >> 8,
                              R3=0, R4=96, R5=0, R6=96, R7=1)
                        c, _ = q.invoke('MetaspriteRenderLoop')
                        accepted = offset+length < 256
                        assert bool(c.p & 1) == accepted
                        assert q.get('CurrentOAMOffset') == (offset+length if accepted else offset)
                        capacity.append(dict(variant=variant, face=face, pose=pose, ink=ink,
                                             offset=offset, rotation=rotation, accepted=accepted))
                    rows.append(dict(variant=variant, face=face, pose=pose, ink=ink,
                                     name=name, parts=count, source_pixels=len(pixels)))
                assert combined == original
    paths = [Path(__file__), rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'),
             NATIVE, R/'tools/prepare_river_city_assets.py', R/'tools/prepare_river_city_reference.py',
             R/'tools/prepare_river_city_shared_palette_v3.py',
             R/'src/river_city_shared_palette_art.inc', atlas, metadata, unit, cfg, binary, labels,
             out/'art.dbg']
    proof = dict(passed=True, native_run=False, scope=__doc__, host_ROM_sha256=sha(rom),
                 actual_host_layer_renders=rows, actual_capacity_controls=capacity,
                 complete_source_frames=72, art_bytes=symbols['RcArtEnd']-symbols['RcArtStart'],
                 limits=['Source/assembled host OAM masks and role indices only.',
                         'No live NES palette composition, scene/menu or native gameplay claim.',
                         'The all-area black ink shade remains a separate composition obligation.'],
                 commands=commands, bindings=[dict(path=str(p), sha256=sha(p)) for p in paths])
    (out/'controls.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, layers=len(rows), capacity=len(capacity),
                          source_frames=72, art_bytes=proof['art_bytes'])))


if __name__ == '__main__':
    main()
