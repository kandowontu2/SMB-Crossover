"""Stage source-verified Mike drop halves and late-game Super Nova pixels."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-mike-art-nx')
PARENT_SHA = 'f650bbb4980ad11911eef1a214405191abd17b4f31f1960af3f2d1d7cdc1a402'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with gzip.open(path, 'rt', newline='') as handle:
        return list(csv.DictReader(handle))


def tile_pixels(raw, flip=False):
    result = []
    for y in range(16):
        at = y // 8 * 16 + y % 8
        line = [(raw[at] >> (7 - x) & 1) | (raw[at + 8] >> (7 - x) & 1) << 1
                for x in range(8)]
        result.append(line[::-1] if flip else line)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='candidate-v4')
    args = parser.parse_args()
    out = OUT / args.name; out.mkdir(parents=True, exist_ok=False)
    overlay = out / 'overlay'
    (overlay / 'src').mkdir(parents=True)
    (overlay / 'chr/characters').mkdir(parents=True)
    rom = Path('C:/NES/StarTropics (USA).nes')
    assert sha(rom) == 'ff20d5e9600565ae61e4eae6594c9f1e55e2a748a46bba0c88285140420a219a'
    native = rom.read_bytes()[16 + 262144:]
    def pair(bank, tile):
        return native[bank * 1024 + tile * 16:bank * 1024 + tile * 16 + 32]
    expected = {'heart': pair(205, 12), 'star': pair(205, 14),
                'nova0': pair(205, 32), 'nova1': pair(205, 34)}
    source_cases = {}
    # The actor's native pose81/80 produces two mirrored halves; don't infer
    # a whole icon by guessing a single nearby CHR tile.
    drop = rows(OUT / 'drop-d12-v2/drops.csv.gz')
    for kind, start, stop, tile in (('star', 612, 660, 79), ('heart', 692, 740, 77)):
        cases = []
        for row in drop:
            frame = int(row['frame'])
            if not start <= frame < stop:
                continue
            oam = bytes.fromhex(row['oam'])
            parts = [tuple(oam[i:i + 4]) for i in range(0, 256, 4) if oam[i + 1] == tile and oam[i] < 180]
            assert len(parts) == 2, (kind, frame, parts)
            left, right = sorted(parts, key=lambda part: part[3])
            assert (left[0], left[1], left[2], left[3] + 8) == (right[0], right[1], right[2] ^ 64, right[3])
            assert left[2] == 0 and right[2] == 64
            assert pair(205, (tile & 62)) == expected[kind]
            cases.append(dict(frame=frame, native_OAM_parts=parts))
        assert len(cases) == 48
        source_cases[kind] = cases
    weapon_rows = rows(OUT / 'native-d12-v3/original-weapons-d.csv.gz')
    mapping = rows(OUT / 'native-d12-v3/mapper.csv.gz')
    for tile, name in ((97, 'nova0'), (99, 'nova1')):
        witnesses = []
        for row in weapon_rows:
            if int(row['id']) != 3:
                continue
            oam = bytes.fromhex(row['oam'])
            for i in range(0, 256, 4):
                y, t, attr, x = oam[i:i + 4]
                if t == tile and y < 180:
                    # OAM endFrame snapshots precede the corresponding next
                    # completed screenshot; physical mapping is stable for
                    # these whole source-world attack frames.
                    m = [item for item in mapping if int(item['frame']) == int(row['frame'])
                         and 60 <= int(item['scanline']) < y]
                    assert m and int(m[-1]['r3']) == 205
                    assert pair(205, tile & 62) == expected[name]
                    witnesses.append(dict(frame=int(row['frame']), OAM=[y, t, attr, x], CHR=205))
        assert len(witnesses) >= 6, name
        source_cases[name] = witnesses
    original_asset = ROOT / 'chr/characters/mike-jones.chr'
    original_art = ROOT / 'src/mike_jones_art.inc'
    blob = bytearray(original_asset.read_bytes()); assert len(blob) == 4096
    before = bytes(blob)
    slots = {'heart': 3072 + 19 * 32, 'star': 3072 + 22 * 32,
             'nova0': 2048 + 8 * 32, 'nova1': 2048 + 9 * 32}
    negative = {name: hashlib.sha256(before[offset:offset + 32]).hexdigest()
                for name, offset in slots.items()}
    assert all(before[offset:offset + 32] != expected[name] for name, offset in slots.items())
    for name, offset in slots.items():
        blob[offset:offset + 32] = expected[name]
    art = original_art.read_text()
    for name, tile in (('JnHeart', 103), ('JnStar', 109)):
        old = f'{name}:.byte 4,{tile},2,0,0'
        new = f'{name}:.byte 8,{tile},2,0,0,{tile},66,0,8'
        assert art.count(old) == 1; art = art.replace(old, new)
    # All four pages and table identities stay put; only the four 32-byte
    # source pairs and the two complete 16-pixel metasprites change.
    assert before[:2048] == bytes(blob[:2048])
    allowed = {offset + n for offset in slots.values() for n in range(32)}
    assert all(a == b or i in allowed for i, (a, b) in enumerate(zip(before, blob)))
    target_asset = overlay / 'chr/characters/mike-jones.chr'; target_asset.write_bytes(blob)
    target_art = overlay / 'src/mike_jones_art.inc'; target_art.write_text(art)
    core = (ROOT / 'src/mike_jones_core.s').read_text()
    old = 'Done:sta JnTier\n rts\n.endproc\n.proc JnInputs'
    assert core.count(old) == 1
    core = core.replace(old, 'Done:jmp JnPublishTier\n nop ; preserve all subsequent resident profile addresses\n.endproc\n.proc JnInputs')
    (overlay / 'src/mike_jones_core.s').write_text(core)
    dispatch = (ROOT / 'src/mike_jones_dispatch.s').read_text()
    dispatch += '''
; Publish the effective weapon name after a physical reward or HP gate change.
; This helper is appended in the same A-window bank; the original tier tail
; remains four bytes. Preserve the original caller's A/X/Y/status contract.
.pushseg
.segment "MIKE_CORE"
.proc JnPublishTier
 php
 cmp JnTier
 sta JnTier
 jeq Unchanged
 pha
 lda #1
 sta JnUiDirty
 pla
Unchanged:plp
 rts
.endproc
.popseg
'''
    (overlay / 'src/mike_jones_dispatch.s').write_text(dispatch)
    # ca65 first resolves a nested include beside its parent module. Stage
    # that unchanged parent too, with only its binary path made explicit;
    # otherwise a shallow overlay silently compiles the original root art.
    module = (ROOT / 'src/mike_jones.s').read_text()
    assert module.count('.incbin "chr/characters/mike-jones.chr"') == 1
    module = module.replace('.incbin "chr/characters/mike-jones.chr"',
                            '.incbin "' + target_asset.as_posix() + '"')
    (overlay / 'src/mike_jones.s').write_text(module)
    (overlay / 'smb1base-mmc5-expanded.cfg').write_bytes((ROOT / 'smb1base-mmc5-expanded.cfg').read_bytes())
    cmd = [sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
           '--source-overlay', str(overlay), '--output', str(out / 'candidate.nes')]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    (out / 'build-runner.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    parent = ROOT / 'build/checkpoints/vic-hud-font-nw/candidate.nes'
    assert sha(parent) == PARENT_SHA
    old_rom, new_rom = parent.read_bytes(), (out / 'candidate.nes').read_bytes()
    changed_PRG = [bank for bank in range(128) if old_rom[16 + bank * 8192:16 + (bank + 1) * 8192]
                   != new_rom[16 + bank * 8192:16 + (bank + 1) * 8192]]
    changed_CHR = [bank for bank in range(1024) if old_rom[16 + 1048576 + bank * 1024:16 + 1048576 + (bank + 1) * 1024]
                   != new_rom[16 + 1048576 + bank * 1024:16 + 1048576 + (bank + 1) * 1024]]
    assert changed_PRG == [96, 97, 98] and changed_CHR == [710, 711]
    # Enlarging two art records relocates four later art labels referenced
    # by combat. Check the exact operands instead of calling any bank98
    # difference an allowed gameplay-code change.
    def labels(path):
        result = {}
        for line in path.read_text().splitlines():
            match = re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\w+)', line)
            if match:
                result[match[2]] = int(match[1], 16)
        return result
    parent_labels = labels(parent.with_suffix('.lbl'))
    candidate_labels = labels((out / 'candidate.nes').with_suffix('.lbl'))
    assert all(candidate_labels[name] == value for name, value in parent_labels.items()
               if name.startswith('Jn') and value < 0xc000), 'Keep all existing code/state addresses unchanged'
    refs = {0xa9a3: 'JnShotAllLo', 0xa9a8: 'JnShotAllHi',
            0xaa06: 'JnBigHeart', 0xaa56: 'JnStar'}
    off = 16 + 98 * 8192
    differences = {0xa000 + n for n in range(8192) if old_rom[off + n] != new_rom[off + n]}
    assert differences == set(refs)
    for address, name in refs.items():
        assert old_rom[off + address - 0xa000] == parent_labels[name] & 255
        assert new_rom[off + address - 0xa000] == candidate_labels[name] & 255
        assert parent_labels[name] >> 8 == candidate_labels[name] >> 8
    report = dict(passed=True, parent_ROM_sha256=PARENT_SHA, ROM_sha256=sha(out / 'candidate.nes'),
                  original_ROM_sha256=sha(rom), current_negative_tile_hashes=negative,
                  original_and_staged={p: dict(before=sha(ROOT / p), after=sha(overlay / p))
                     for p in ('src/mike_jones_art.inc', 'chr/characters/mike-jones.chr',
                               'src/mike_jones_core.s', 'src/mike_jones_dispatch.s')},
                  source_pairs={name: hashlib.sha256(value).hexdigest() for name, value in expected.items()},
                  overlay_parent_wrapper_sha256=sha(overlay / 'src/mike_jones.s'),
                  source_cases=source_cases, changed_PRG_banks=changed_PRG, changed_CHR_pages=changed_CHR,
                  combat_only_changes_are_relocated_art_operands=refs,
                  installed_sources_changed=False,
                  limits=['Shared SMB item palette2 remains the declared hue adaptation.',
                          'The debug/inventory/source-drop arrangements are component fixtures, not original campaign routes.',
                          'Other Mike weapon art/behaviors and the final roster/powerup matrix are not certified by this local proof.'])
    (out / 'source-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'source_cases'}))


if __name__ == '__main__':
    main()
