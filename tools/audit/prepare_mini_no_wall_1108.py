"""Reassemble the installed Mini kernel without the host wall-jump adaptation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from prepare_prince_resume_1108 import CURRENT
from prepare_selected_native_packet_v1 import R, sha

BASE = R/'build/mini-two-fireballs-1103/mini-empty-draw.nes'
KERNEL = BASE.with_name('mini-zero.s')
LINKER = R/'build/mini-mario-power-contract-1103-v51/mini-host-v56.cfg'
CODE = 1048592 + 962*1024
COOKIE = 16 + 65*8192 + 0x1003
CALL = 0xb068 - 0xa000
WORKER = slice(0xb0fb-0xa000, 0xb13b-0xa000)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    assert sha(BASE) == CURRENT
    original = BASE.read_bytes()
    old_kernel = KERNEL.with_suffix('.bin').read_bytes()
    assert len(old_kernel) == 5120 and original[CODE:CODE+5120] == old_kernel
    assert old_kernel[CALL:CALL+3] == bytes.fromhex('20fbb0')
    assert old_kernel[WORKER].startswith(bytes.fromhex('ad4cc22901d038'))
    assert original[COOKIE+3:COOKIE+16] == hashlib.sha256(original[CODE:CODE+7168]).digest()[:13]

    source = KERNEL.read_text()
    old = ' jsr MiniHostWallJump\n jsr MiniAnimate\n'
    assert source.count(old) == 1
    source = source.replace(old, ' jmp MiniHostAnimate\nMiniHostAnimate:\n jsr MiniAnimate\n')
    start = source.index('; Explicit user-authorized native adaptation. Uses original queued jump pulse.')
    end = source.index('MiniHostImportX:', start)
    source = source[:start] + ' .res 64,$ff ; Former wall grab worker.\n\n' + source[end:]

    output.mkdir()
    asm = output/'mini-no-wall.s'
    asm.write_text(source, encoding='utf-8', newline='\n')
    binary = asm.with_suffix('.bin')
    obj = asm.with_suffix('.o')
    labels = asm.with_suffix('.lbl')
    compiler = R/'tools/Windows/cc65/bin'
    subprocess.run([compiler/'ca65.exe', asm, '-o', obj], check=True)
    subprocess.run([compiler/'ld65.exe', '-C', LINKER, obj, '-o', binary, '-Ln', labels], check=True)
    data = binary.read_bytes()
    expected = bytearray(old_kernel)
    expected[CALL:CALL+3] = bytes.fromhex('4c6bb0')
    expected[WORKER] = b'\xff'*64
    assert data == expected, 'Only the wall-grab call and its retired worker may change'
    assert labels.read_bytes() == KERNEL.with_suffix('.lbl').read_bytes()

    raw = bytearray(original)
    raw[CODE:CODE+5120] = data
    raw[COOKIE+3:COOKIE+16] = hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    rom = asm.with_suffix('.nes')
    rom.write_bytes(raw)
    # The component's labels above belong to the controller. The full ROM
    # debugger uses the unchanged parent labels and their original basename.
    game = output/'candidate.nes'
    rom.rename(game)
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(suffix), game.with_suffix(suffix))
    report = dict(candidate_SHA256=sha(game), parent_SHA256=CURRENT,
                  kernel_SHA256=sha(binary), helper_platforms_added=False,
                  changes=['Remove post-MiniStep wall cling and airborne re-jump',
                           'Keep original source jump, collision and animation addresses',
                           'Retire exact 64-byte Mini kernel worker and rebind its owner cookie'],
                  bindings={str(p):sha(p) for p in (BASE,KERNEL,LINKER,Path(__file__))})
    (output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
