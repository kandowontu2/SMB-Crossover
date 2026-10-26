"""Fuse the genuine shot caller setup; retain literal uncommon rendering."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, sha

PARENT = '8d60280ccec6cea4a7544cd1745bae03598fee2c05b736877e166dc1d42e1184'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['parent', 'output']: p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert sha(a.parent / 'candidate.nes') == PARENT
    assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    old = load(a.parent / 'candidate.nes')
    tail = 16 + 87 * 8192 + 0x1c8d
    assert old['raw'][tail:16 + 88 * 8192] == b'\xff' * (0xc000 - 0xbc8d)
    assert address(old, 'TnExactShurikenRender') + int(old['syms']['TnExactShurikenRender']['size'], 0) == 0xbc8d
    a.output.mkdir(parents=True)
    s = a.output / 'source'
    shutil.copytree(a.parent / 'source', s, ignore=shutil.ignore_patterns('__pycache__'))
    p = s / 'src/tmnt_equipment_draw.s'
    text = p.read_text()
    anchor = 'ShotPointer:\n ldy TnShotFace,x\n'
    assert text.count(anchor) == 1
    p.write_text(text.replace(anchor, 'ShotPointer:\n jmp TnShotOwnerScope\n'))
    p = s / 'src/tmnt.s'
    text = p.read_text()
    anchor = '.include "tmnt_equipment_shuriken_fast.s"'
    assert text.count(anchor) == 1
    p.write_text(text.replace(anchor, anchor + '\n.include "tmnt_equipment_shot_scope.s"'))
    lines = ['; Actual ShotPointer entry: X=slot, A=nonzero original source pose.',
             '; No extra renderer admission on uncommon poses. Scratch world/page',
             '; subtraction is performed directly; its discarded input copies vanish.',
             '.pushseg', '.segment "TN_EQUIP_FAST"', '.proc TnShotOwnerScope',
             ' cmp #73', ' beq Select0', ' cmp #74', ' beq Select1',
             ' cmp #75', ' beq Select2',
             'Legacy:', ' tay', ' lda TnShotFace,x', ' cmp #2', ' beq Left',
             ' lda TnWorldRLo,y', ' sta R0', ' lda TnWorldRHi,y', ' sta R1', ' jmp Coordinate',
             'Left:', ' lda TnWorldLLo,y', ' sta R0', ' lda TnWorldLHi,y', ' sta R1',
             'Coordinate:', ' sec', ' lda TnShotX,x', ' sbc ScreenLeft_X_Pos', ' sta R4',
             ' lda TnShotPage,x', ' sbc ScreenLeft_PageLoc', ' sta R5',
             ' lda TnShotY,x', ' sta R6', ' lda #1', ' sta R7', ' lda #0', ' sta R3',
             ' jsr TnWorldDraw', ' jmp TnDrawEquipment::NextShot']
    for n in range(3):
        lines += [f'Select{n}:', ' ldy TnShotFace,x', ' cpy #2', f' beq Left{n}',
                  f' jmp Path{n}', f'Left{n}:', f' jmp Path{n+3}']
    records = []
    for n, (face, pose) in enumerate([(f, p) for f in ['R', 'L'] for p in range(73, 76)]):
        lo, hi = location(old, 'TnWorld' + face + 'Lo'), location(old, 'TnWorld' + face + 'Hi')
        ptr = old['raw'][lo + pose] + 256 * old['raw'][hi + pose]
        records.append(dict(index=n, face=face, pose=pose, pointer=ptr))
        lines += [f'Path{n}:', f' lda #${ptr & 255:02x}', ' sta R0',
                  f' lda #${ptr >> 8:02x}', ' sta R1',
                  ' sec', ' lda TnShotX,x', ' sbc ScreenLeft_X_Pos', ' sta R4',
                  ' lda TnShotPage,x', ' sbc ScreenLeft_PageLoc', ' sta R5',
                  f' bne PageLegacy{n}', ' php', ' lda TnShotY,x', ' sta R6',
                  ' cmp #24', f' bcc RestoreLegacy{n}', ' lda R4', ' cmp #8', f' bcc RestoreLegacy{n}',
                  ' lda CurrentOAMOffset', ' cmp #248', f' bcs RestoreLegacy{n}', ' plp',
                  ' lda #1', ' sta R7', ' lda #0', ' sta R3',
                  f' jsr TnExactShurikenRender::Record{n}', ' jmp TnDrawEquipment::NextShot',
                  f'RestoreLegacy{n}:', ' plp', f'LegacyAfterY{n}:',
                  ' lda #1', ' sta R7', ' lda #0', ' sta R3', ' jsr TnWorldDraw',
                  ' jmp TnDrawEquipment::NextShot', f'PageLegacy{n}:',
                  ' lda TnShotY,x', ' sta R6', f' jmp LegacyAfterY{n}']
    lines += ['.endproc', '.assert TnShotOwnerScope=$bc8d,lderror,"Verified new A87 tail"',
              '.assert *<=$c000,lderror,"Keep bank87 bounded"', '.export TnShotOwnerScope', '.popseg', '']
    (s / 'src/tmnt_equipment_shot_scope.s').write_text('\n'.join(lines))
    cmd = [sys.executable, '-B', str(s / 'tools/build_mmc5_expanded.py'), '--workspace', str(s),
           '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    r = subprocess.run(cmd, cwd=s, capture_output=True, text=True)
    (a.output / 'build.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (r.stdout + r.stderr)[-5000:]
    new = load(a.output / 'candidate.nes')
    assert qualified(a.parent / 'candidate.nes').items() <= qualified(a.output / 'candidate.nes').items()
    bank = lambda raw, n: raw[16+n*8192:16+(n+1)*8192]
    delta = {n: sum(x != y for x, y in zip(bank(old['raw'], n), bank(new['raw'], n))) for n in range(128)}
    delta = {n: v for n, v in delta.items() if v}
    assert set(delta) == {87}
    assert old['raw'][:16] == new['raw'][:16] and old['raw'][1048592:] == new['raw'][1048592:]
    assert bank(old['raw'], 87)[0x1500:0x1c8d] == bank(new['raw'], 87)[0x1500:0x1c8d]
    manifest = {}; patch = ''
    for name in ['src/tmnt.s', 'src/tmnt_equipment_draw.s', 'src/tmnt_equipment_shot_scope.s']:
        p, q = a.parent / 'source' / name, s / name
        manifest[name] = dict(before_sha256=sha(p) if p.exists() else None, after_sha256=sha(q))
        patch += ''.join(difflib.unified_diff(p.read_text().splitlines(True) if p.exists() else [], q.read_text().splitlines(True), fromfile='a/'+name, tofile='b/'+name))
    (a.output / 'review.patch').write_text(patch)
    for filename in ['preparation.json', 'fast-preparation.json']:
        if (a.parent / filename).exists():
            prep = json.loads((a.parent / filename).read_text()); prep['candidate_ROM_sha256'] = sha(a.output / 'candidate.nes')
            (a.output / filename).write_text(json.dumps(prep, indent=2) + '\n')
    q = dict(prepared=True, source_only=True, native_run=False, accepted=False,
             parent_ROM_sha256=PARENT, candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
             verified_preexisting_FF_tail=[0xbc8d, 0xc000], helper_size=int(new['syms']['TnShotOwnerScope']['size'], 0),
             changed_PRG_bytes=delta, all_old_qualified_symbols_exact=True, original_record_bindings=records,
             literal_uncommon_TnWorldDraw=True, changed_intermediate_private_scratch='Initial R4/R5 input copies omitted; Y holds source pose during table lookup. Full caller/output/IRQ liveness qualification remains required.',
             source_changes=manifest, checker_sha256=sha(Path(__file__)))
    (a.output / 'shot-scope-preparation.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q))


if __name__ == '__main__': main()
