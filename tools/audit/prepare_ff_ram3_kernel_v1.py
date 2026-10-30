"""Assemble an offline FF RAM3 execution image; allocate no cartridge resources."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies

P = R/'build/final-fantasy-current-component-v2'
O = R/'build/final-fantasy-ram3-kernel-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(value, newline='\n')


if __name__ == '__main__':
    assert not O.exists()
    parent_path = P/'cpu-controls-v1/controls.json'
    assert sha(parent_path) == 'dd13e588942a0d79a201c183b99cb5ab33d5e4d8a5c45d4f834aaeb0021a2e01'
    parent = json.loads(parent_path.read_text())
    assert parent['passed']
    for path, digest in parent['bindings'].items():
        assert sha(path) == digest, path
    base = qualified(P/'linked/candidate.nes')
    O.mkdir()
    source = (P/'linked/ff-component.s').read_text()
    assert source.count('.import X5SetPhysicalChr\n') == 1
    source = source.replace('.import X5SetPhysicalChr\n',
                            '.import FfRamPhysicalChr\n.define X5SetPhysicalChr FfRamPhysicalChr\n')
    write(O/'component.s', source)
    native_source = [Path(p) for p in parent['bindings'] if Path(p).name == 'mmc5_expanded.s']
    assert len(native_source) == 1
    native = native_source[0].read_text()
    start, stop = native.index('X5SetPhysicalChr:'), native.index('X5SetSpecialChr:')
    publisher = native[start:stop].replace('X5SetPhysicalChr:', 'FfRamPhysicalChr:')
    write(O/'publisher.s', '.import CurrentCHRBank,X5ChrMode,X5WideChrActive,ReloadCHRBank\n'
          '.segment "FF_RAM_PUBLISHER"\n.export FfRamPhysicalChr,FfRamPhysicalChrEnd\n'+publisher+'FfRamPhysicalChrEnd:\n')
    definitions = []
    for line in source.splitlines():
        match = re.fullmatch(r'\.import(zp)? (\w+)', line)
        if not match or match[2] == 'FfRamPhysicalChr':
            continue
        zp, name = match.groups()
        definitions += ['.export'+('zp ' if zp else ' ')+name,
                        name+'='+base['syms'][name]['val'].replace('0x', '$')]
    write(O/'host-definitions.s', '; Actual current host ABI for an offline image only.\n'+'\n'.join(definitions)+'\n')
    cfg = 'MEMORY {\n'
    cfg += 'RAM3:start=$a000,size=$2000,bank=3,file="'+(O/'ram3.bin').as_posix()+'",fill=yes,fillval=$ff;\n'
    cfg += 'ART:start=$d000,size=$1000,bank=93,file="'+(O/'art.bin').as_posix()+'";\n'
    cfg += 'CHR:start=$bd000,size=$8000,file="'+(O/'art.chr').as_posix()+'";\n}\n'
    cfg += 'SEGMENTS {\nFF_RAM_PUBLISHER:load=RAM3,type=ro,start=$a275;\n'
    cfg += 'FINAL_FANTASY_CORE:load=RAM3,type=ro,start=$aa00;\n'
    cfg += 'FINAL_FANTASY_ART:load=ART,type=ro;\nFINAL_FANTASY_CHR:load=CHR,type=ro;\n}\n'
    write(O/'kernel.cfg', cfg)
    ca = R/'tools/Windows/cc65/bin/ca65.exe'
    logs = []
    commands = [[str(ca), '-g', '--cpu', '6502x', '-I', str(R/'src'),
                 '--bin-include-dir', str(R), '--create-full-dep', str(O/(name+'.d')),
                 '-o', str(O/(name+'.o')), str(O/(name+'.s'))]
                for name in ['component', 'publisher', 'host-definitions']]
    commands += [[str(ca.with_name('ld65.exe')), '-C', str(O/'kernel.cfg'),
                  '--dbgfile', str(O/'kernel.dbg'), '-Ln', str(O/'kernel.lbl'),
                  '-m', str(O/'kernel.map'), '-o', str(O/'unused-output.bin'),
                  *[str(O/(name+'.o')) for name in ['component', 'publisher', 'host-definitions']]]]
    for command in commands:
        result = subprocess.run(command, cwd=R, capture_output=True, text=True)
        logs.append(dict(command=command, returncode=result.returncode,
                         stdout=result.stdout, stderr=result.stderr))
        write(O/'compile-log.json', json.dumps(logs, indent=2)+'\n')
        assert result.returncode == 0, result.stderr[-12000:]
    image = (O/'ram3.bin').read_bytes()
    assert len(image) == 8192
    old = base['raw']
    assert image[0xa00:0xa00+3211] == old[16+62*8192+0xa00:16+62*8192+0xa00+3211]
    assert image[0x275:0x275+20] == old[16+62*8192+0x275:16+62*8192+0x275+20]
    assert (O/'art.bin').read_bytes() == (R/'build/final-fantasy-component-v1/art.bin').read_bytes()
    assert (O/'art.chr').read_bytes() == (R/'build/final-fantasy-component-v1/chr.bin').read_bytes()
    occupied = set(range(0x275, 0x289)) | set(range(0xa00, 0xa00+3211))
    assert all(value == 255 for i, value in enumerate(image) if i not in occupied)
    bindings = dict(parent['bindings'])
    files = {Path(__file__).resolve(), parent_path, native_source[0]}
    for name in ['component', 'publisher', 'host-definitions']:
        files.update(dependencies(O/(name+'.d')))
    files.update(path for path in O.iterdir() if path.is_file())
    bindings.update({str(path.resolve()):sha(path) for path in files})
    report = dict(passed=True, status='OFFLINE_RAM3_IMAGE_ONLY_NO_RESOURCE_ALLOCATION',
                  current_host_ROM_sha256=sha(P/'linked/candidate.nes'),
                  image_sha256=sha(O/'ram3.bin'), virtual_bank=3, virtual_window='A000..BFFF',
                  source_CORE_byte_exact=True, native_publisher_byte_exact=True,
                  CORE_bytes=3211, publisher_bytes=20, source_ART_CHR_exact=True,
                  unused_image_bytes=8192-len(occupied),
                  prospective_cookie='BFE0..<BFF0 not yet initialized or allocated',
                  limits=['No game/header/PRG/CHR/WRAM reservation or native run is implied.',
                          'Real loader, raw-bank Main/NMI/IRQ, cache lifecycle and host adapters remain required.',
                          'A physical CHR carrier is conditional on the genuine dense Parodius source composition.'],
                  bindings=bindings)
    write(O/'build-proof.json', json.dumps(report, indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['status','image_sha256','CORE_bytes','publisher_bytes','unused_image_bytes']}))
