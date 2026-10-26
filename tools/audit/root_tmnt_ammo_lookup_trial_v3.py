"""Build a private, same-address turtle ammo decimal lookup trial."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys

from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load, location
from tmnt_native_storage_driver import ROOT, sha

PARENT = '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert sha(a.parent / 'candidate.nes') == PARENT
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.parent / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    path = source / 'src/tmnt_equipment_draw.s'
    text = path.read_text()
    old = ' lda #0\n sta TnTempX\n sta TnTempY\n lda TnTemp2\nHundreds:'
    new = '''.if ::MAPPER_MMC5
 jmp ::TnAmmoDecimalLookup
 .res 2,$ea ; original five-byte LDA/STA footprint
.else
 lda #0
 sta TnTempX
.endif
 sta TnTempY
 lda TnTemp2
Hundreds:'''
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    helper = '''; Private MMC5 lookup. Keep the caller's X queue offset and Y intact.
; The ones store is the literal first Digits store; return to the following
; instruction. Original inner labels and the entire commit path stay fixed.
.pushseg
.segment "TMNT_CORE"
.res $e0,$ff ; parent TMNT_CORE ends atB020
.proc TnAmmoDecimalLookup
 tya
 pha
 ldy TnTemp2
 lda Hundreds,y
 sta TnTempX
 lda Tens,y
 sta TnTempY
 lda Ones,y
 sta VRAM_Buffer1+5,x
 pla
 tay
 jmp ::TnAmmoHud::Digits+3
.assert TnAmmoDecimalLookup=$b100,lderror,"Private unused tail only"
.align $100,$ff
Hundreds:
'''
    for name, values in [('Hundreds', [n // 100 for n in range(256)]),
                         ('Tens', [(n // 10) % 10 for n in range(256)]),
                         ('Ones', [n % 10 for n in range(256)])]:
        if name != 'Hundreds': helper += name + ':\n'
        for start in range(0, 256, 16):
            helper += ' .byte ' + ','.join(str(n) for n in values[start:start + 16]) + '\n'
    helper += '.endproc\n.export TnAmmoDecimalLookup\n.popseg\n'
    (source / 'src/tmnt_ammo_decimal_lookup.s').write_text(helper)
    entry = source / 'src/entrypoint.s'
    entry.write_text(entry.read_text() + '\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "tmnt_ammo_decimal_lookup.s"\n.endif\n')
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
               '--output', str(a.output / 'candidate.nes')]
    result = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-5000:]
    oldrom, newrom = (a.parent / 'candidate.nes').read_bytes(), (a.output / 'candidate.nes').read_bytes()
    oldq, newq = qualified(a.parent / 'candidate.nes'), qualified(a.output / 'candidate.nes')
    assert oldq.items() <= newq.items()
    bundle = load(a.parent / 'candidate.nes')
    hook = location(bundle, 'TnAmmoHud')
    newbundle = load(a.output / 'candidate.nes')
    target = location(newbundle, 'TnAmmoDecimalLookup')
    end = 16 + 87 * 8192 + 0x1500
    assert target == 16 + 87 * 8192 + 0x1100
    assert oldrom[target:end] == bytes([255]) * (end - target)
    changed = [i for i, (x, y) in enumerate(zip(oldrom, newrom)) if x != y]
    assert changed and {((i - 16) // 8192) for i in changed} == {87}
    assert all(hook <= i < hook + 256 or target <= i < end for i in changed)
    assert oldrom[:16] == newrom[:16] and oldrom[1048592:] == newrom[1048592:]
    patch = ''
    sources = {}
    for name in ['src/tmnt_equipment_draw.s', 'src/entrypoint.s', 'src/tmnt_ammo_decimal_lookup.s']:
        before, after = a.parent / 'source' / name, source / name
        sources[name] = {'before_sha256': sha(before) if before.exists() else None, 'after_sha256': sha(after)}
        patch += ''.join(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],
                        after.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'review.patch').write_text(patch)
    proof = dict(prepared=True, source_only=True, native_run=False, accepted=False,
                 parent_ROM_sha256=PARENT, candidate_ROM_sha256=sha(a.output / 'candidate.nes'),
                 changed_ROM_bytes=len(changed), changed_bank=87, existing_qualified_symbols_exact=True,
                 all_audio_other_banks_CHR_exact=True, new_RAM=False, hardware_math=False,
                 helper_file_offset=target, hook_routine_file_offset=hook,
                 source_changes=sources, builder_sha256=sha(Path(__file__)))
    (a.output / 'preparation.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
