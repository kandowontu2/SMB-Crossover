"""Stage an isolated TMNT empty-equipment drawing optimization from NY."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-performance-nz')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--label', required=True)
    a = p.parse_args(); assert a.label and all(c.isalnum() or c in '-_' for c in a.label)
    out = OUT / a.label; out.mkdir(parents=True, exist_ok=False)
    parent = ROOT / 'build/checkpoints/tmnt-equipment-ny'
    manifest = json.loads((parent / 'manifest.json').read_text())
    assert sha(parent / 'candidate.nes') == manifest['rom_sha256']
    source = out / 'source'
    with zipfile.ZipFile(parent / 'source.zip') as z:
        assert z.testzip() is None
        assert all((source / n).resolve().is_relative_to(source.resolve()) for n in z.namelist())
        z.extractall(source)
    assert all(sha(source / n) == h for n, h in manifest['source_files'].items())
    file = source / 'src/tmnt_equipment_draw.s'; before = sha(file); text = file.read_text()
    old = ''' lda #.lobyte(628)
 ldx #.hibyte(628)
 farcall X5SetSpecialChr
 BankPRGC #.bank(TnWorldArtStart)
 ldx #2
'''
    new = ''' ; Same publication stores/order as X5SetSpecialChr, without a bank trip.
 lda #.lobyte(628)
 sta SsChrPhysical
 lda #.hibyte(628)
 sta X5SpecialChrUpper
 lda #1
 sta SsChrActive
 sta X5WideChrActive
 sta ReloadCHRBank
 BankPRGC #.bank(TnWorldArtStart)
 ; Inactive slots cannot produce source sprites. Retain the old ammo HUD
 ; path and its final scratch slot even when there is nothing to scan.
 lda TnGearSelected
 ora TnShotKind
 ora TnShotKind+1
 ora TnShotKind+2
 ora TnDropKind
 ora TnDropKind+1
 ora TnDropKind+2
 ora TnDropKind+3
 ora TnPickupStamp
 ora TnPickupStamp+1
 ora TnPickupStamp+2
 ora TnPickupStamp+3
 ora TnPickupStamp+4
 ora TnPickupStamp+5
 bne RenderActors
 lda #0
 sta TnDrawSlot
 ldx #$ff
 jmp Ammo
RenderActors:
 ldx #2
'''
    assert text.count(old) == 1; file.write_text(text.replace(old, new))
    result = subprocess.run([sys.executable, str(source / 'tools/build_mmc5_expanded.py'),
        '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
        '--output', str(out / 'candidate.nes')], cwd=source, capture_output=True, text=True)
    (out / 'build.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr
    old_rom = (parent / 'candidate.nes').read_bytes(); new_rom = (out / 'candidate.nes').read_bytes()
    changed_banks = [i for i in range(128) if old_rom[16+i*8192:16+(i+1)*8192] != new_rom[16+i*8192:16+(i+1)*8192]]
    assert changed_banks == [78, 87, 89, 93], changed_banks
    def labels(path):
        return {q[2][1:]:int(q[1],16) for line in path.read_text().splitlines()
                if len(q:=line.split())==3 and q[0]=='al'}
    old_labels=labels(parent/'candidate.lbl'); new_labels=labels(out/'candidate.lbl')
    references={78:('TnQueuePalette', {559:0,564:8}), 93:('TnGraphics',{1133:0})}
    relocations=[]
    for bank,(name,operands) in references.items():
        actual={i for i in range(8192) if old_rom[16+bank*8192+i]!=new_rom[16+bank*8192+i]}
        assert actual==set(operands), (bank,actual)
        for offset,shift in operands.items():
            at=16+bank*8192+offset
            assert old_rom[at-1]==new_rom[at-1]==0xa9
            assert old_rom[at]==old_labels[name]>>shift&255
            assert new_rom[at]==new_labels[name]>>shift&255
        relocations.append(dict(bank=bank,target=name,old=old_labels[name],new=new_labels[name],operand_offsets=operands))
    assert old_rom[16+1048576:] == new_rom[16+1048576:]
    report = dict(passed=True, ROM_sha256=sha(out / 'candidate.nes'), parent_ROM_sha256=manifest['rom_sha256'],
                  source_changes={'src/tmnt_equipment_draw.s': {'before':before, 'after':sha(file)}},
                  changed_PRG_banks=changed_banks, verified_existing_call_relocations=relocations, all_CHR_bytes_unchanged=True,
                  scope='Isolated source candidate only; native differential/performance acceptance pending.')
    (out / 'source-proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
