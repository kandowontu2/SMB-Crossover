"""Remove repeated Mini scan-coordinate copies and unroll the pixel conversion."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from prepare_mini_no_wall_1108 import BASE, CODE, COOKIE, KERNEL, LINKER
from prepare_selected_native_packet_v1 import R, sha


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def convert(source):
    assert source.count('jsr MiniQuery\n') == 2
    source = source.replace('jsr MiniQuery\n', 'jsr MiniNativeTile\n')
    source = once(source, 'MiniScanX = $C274\nMiniScanY = $C276',
                  'MiniScanX = MiniQueryX\nMiniScanY = MiniQueryY')
    start = source.index('MiniQuery:\n')
    end = source.index('MiniHeadEvent:\n', start)
    source = source[:start] + '''MiniToPixelFast:
    ; The old scan-copy worker occupied these same 27 bytes. Move the high
    ; byte through A but keep the public subroutine's A, X, Y and flags.
    pha
    lda MiniCoord+1
    .repeat 4
      lsr a
      ror MiniCoord
    .endrepeat
    sta MiniCoord+1
    pla
    ldx #0
    rts
    .assert *-MiniToPixelFast=27,error,"Former Mini query span"

''' + source[end:]
    return once(source, '''MiniToPixel:
    ldx #4
@shift:
    lsr MiniCoord+1
    ror MiniCoord
    dex
    bne @shift
    rts
''', '''MiniToPixel:
    jmp MiniToPixelFast
    .res 9,$ff
''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--kernel', type=Path, default=KERNEL)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    raw = bytearray(args.base.read_bytes())
    old = args.kernel.with_suffix('.bin').read_bytes()
    assert len(old) == 5120 and raw[CODE:CODE+5120] == old
    assert raw[COOKIE+3:COOKIE+16] == hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    output.mkdir()
    asm = output/'mini-fast.s'
    asm.write_text(convert(args.kernel.read_text()), encoding='utf-8', newline='\n')
    binary, obj, labels = (asm.with_suffix(ext) for ext in ('.bin','.o','.lbl'))
    compiler = R/'tools/Windows/cc65/bin'
    subprocess.run([compiler/'ca65.exe', asm, '-o', obj], check=True)
    subprocess.run([compiler/'ld65.exe', '-C', LINKER, obj, '-o', binary, '-Ln', labels], check=True)
    data = binary.read_bytes()
    assert len(data) == len(old)
    assert labels.read_bytes() == args.kernel.with_suffix('.lbl').read_bytes()
    raw[CODE:CODE+5120] = data
    raw[COOKIE+3:COOKIE+16] = hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    game = output/'candidate.nes'
    game.write_bytes(raw)
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(args.base.with_suffix(ext), game.with_suffix(ext))
    report = dict(candidate_SHA256=sha(game), parent_SHA256=sha(args.base),
                  changed_kernel_bytes=sum(a!=b for a,b in zip(old,data)),
                  kernel_SHA256=sha(binary), source_scan_aliases=['C2E0','C2E2'],
                  bindings={str(p):sha(p) for p in (args.base,args.kernel,LINKER,Path(__file__))})
    (output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
