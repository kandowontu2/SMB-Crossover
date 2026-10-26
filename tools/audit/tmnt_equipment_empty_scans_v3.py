"""Private MMC5 empty-equipment scan gate on frozen parser9a791 only."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, CURRENT, sha


PARENT = '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
HELPER = '''; Guard only the provably empty BOTH-groups case. Every nonzero flag or
; private stamp resumes literal original loops and their original visible work.
; No RAM borrow or foreground hardware math. Icon/ammo code supplies final ABI.
.if ::MAPPER_MMC5
.pushseg
.segment "TMNT_CORE"
.proc TnSkipEmptyEquipmentScans
 ldx TnDrawSlot
 dex
 bmi CheckEmpty
 jmp ::TnDrawEquipment::Shot
CheckEmpty:
 lda TnDropKind
 ora TnDropKind+1
 ora TnDropKind+2
 ora TnDropKind+3
 bne Original
 lda TnPickupStamp
 ora TnPickupStamp+1
 ora TnPickupStamp+2
 ora TnPickupStamp+3
 ora TnPickupStamp+4
 ora TnPickupStamp+5
 bne Original
 lda #0
 sta TnDrawSlot
 ldx #$ff
 jmp TnEquipmentIconResume
Original:
 jmp TnEquipmentScansResume
.endproc
.assert TnSkipEmptyEquipmentScans=$b020,lderror,"Append within unallocated TMNT_CORE tail"
.export TnSkipEmptyEquipmentScans,TnEquipmentScansResume,TnEquipmentIconResume
.popseg
.endif
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.ready / 'receipt.json') == 'db59fddc3479507ea5eb9891a786ad05ff7ef7dd33fb5ed505c18eefbb64d478'
    assert sha(a.ready / 'candidate.nes') == PARENT
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    shutil.copytree(a.ready / 'source', source, ignore=shutil.ignore_patterns('__pycache__'))
    path = source / 'src/tmnt_equipment_draw.s'
    text = path.read_text()
    old = 'NextShot:ldx TnDrawSlot\n dex\n jpl Shot\n ldx #3\nDrop:'
    new = '''NextShot:
.if ::MAPPER_MMC5
 jmp ::TnSkipEmptyEquipmentScans
 .res 3,$ea
.else
 ldx TnDrawSlot
 dex
 jpl Shot
.endif
::TnEquipmentScansResume:
 ldx #3
Drop:'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    old = ' ; An icon and three background digits are visible only while secondary is active.\n'
    assert text.count(old) == 1
    text = text.replace(old, '::TnEquipmentIconResume:\n' + old)
    path.write_text(text)
    path = source / 'src/entrypoint.s'
    text = path.read_text()
    assert text.rstrip().endswith('.endif')
    path.write_text(text + '\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "tmnt_empty_equipment_scans.s"\n.endif\n')
    (source / 'src/tmnt_empty_equipment_scans.s').write_text(HELPER)
    command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / 'candidate.nes')]
    result = subprocess.run(command, cwd=source, capture_output=True, text=True)
    (a.output / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    before, after = (a.ready / 'candidate.nes').read_bytes(), (a.output / 'candidate.nes').read_bytes()
    changes = {n: sum(x != y for x, y in zip(before[16 + n * 8192:16 + (n + 1) * 8192], after[16 + n * 8192:16 + (n + 1) * 8192])) for n in range(128)}
    changes = {n: count for n, count in changes.items() if count}
    assert set(changes) == {87}
    assert before[:16] == after[:16] and before[1048592:] == after[1048592:]
    assert qualified(a.ready / 'candidate.nes').items() <= qualified(a.output / 'candidate.nes').items()
    assert before[16 + 87 * 8192 + 0x1020:16 + 88 * 8192] == bytes([255]) * (8192 - 0x1020)
    prep = json.loads((a.ready / 'preparation.json').read_text())
    prep.update(candidate_ROM_sha256=sha(a.output / 'candidate.nes'), empty_equipment_parent_ROM_sha256=PARENT)
    (a.output / 'preparation.json').write_text(json.dumps(prep, indent=2) + '\n')
    manifest, patch = {}, ''
    for name in ['src/entrypoint.s', 'src/tmnt_equipment_draw.s', 'src/tmnt_empty_equipment_scans.s']:
        old, new = a.ready / 'source' / name, source / name
        manifest[name] = dict(before_sha256=sha(old) if old.exists() else None, after_sha256=sha(new))
        patch += ''.join(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [], new.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    (a.output / 'review.patch').write_text(patch)
    proof = dict(prepared=True, accepted=False, source_only=True, native_run=False,
                 production_parent_ROM_sha256=CURRENT, donor_ROM_sha256=PARENT,
                 candidate_ROM_sha256=sha(a.output / 'candidate.nes'), changed_PRG_bytes=changes,
                 source_changes=manifest, all_existing_qualified_symbols_exact=True,
                 new_RAM_or_hardware_math=False, all_other_banks_audio_CHR_exact=True,
                 old_populated_scan_bodies_retained=True, skip_requires_all_four_flags_and_all_six_stamps_zero=True,
                 checker_sha256=sha(Path(__file__)))
    (a.output / 'scan-preparation.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
