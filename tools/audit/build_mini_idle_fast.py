"""Build the Mini-only idle optimization over the hash-pinned MMC5 nightly."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from build_mini_frame_auth_1103 import PARENT, ROM
from prepare_selected_native_packet_v1 import R, sha
from profile_mini_mario_1103 import KERNEL


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert sha(ROM) == PARENT
    out = args.output.resolve()
    out.mkdir()
    cc = R/'tools/Windows/cc65/bin'
    raw = bytearray(ROM.read_bytes())
    patches = []

    def assemble(sources, cfg, name, labels=False):
        objects = []
        for source in sources:
            obj = out/(source.stem+'.o')
            subprocess.run([cc/'ca65.exe', source, '-o', obj], check=True)
            objects.append(obj)
        output = out/(name+'.bin')
        command = [cc/'ld65.exe', '-C', cfg, *objects, '-o', output]
        if labels:
            command += ['-Ln', out/(name+'.lbl')]
        subprocess.run(command, check=True)
        return output

    def patch(at, old, data, name):
        assert len(old) == len(data) and raw[at:at+len(old)] == old, name
        raw[at:at+len(old)] = data
        patches.append(dict(role=name, offset=at, before=old.hex(), after=data.hex()))

    owner = R/'build/mini-mario-owner-1103-v15'
    selector = (owner/'selector-v15.s').read_text()
    selector = selector.replace('.segment "EX_SELECT"', '.import MiniTry\n.export MiniFullCheck,MiniAuthorized\n.segment "EX_SELECT"')
    selector = selector.replace('PrOdd:\n jsr CoCheckCode\n bcc DkLocalNo\n',
        'PrOdd:\n cmp #4\nMiniBranch:\n .byte $f0, <($a738-($a740+(MiniBranch-ExDispatch)+2))\n'
        'MiniFullCheck:\n jsr CoCheckCode\n bcc DkLocalNo\nMiniAuthorized:\n')
    before = ''' sbc #<ShServiceVeneers
 sta FarcallJmpTarget_SMC+1
 lda FarcallJmpTarget_SMC+2
 sbc #>ShServiceVeneers
 bne DkLocalNo
 lda FarcallJmpTarget_SMC+1
 cmp #111
 bcs DkLocalNo
'''
    after = ''' sbc #<ShServiceVeneers
 bcc DkLocalNo
 cmp #111
 bcs DkLocalNo
 sta FarcallJmpTarget_SMC+1
'''
    assert selector.count(before) == 1
    selector = selector.replace(before, after)
    # PrSh enters only when the target high byte already equals $AA.
    # The compaction pays for the Mini-only branch without moving DkCookie.
    selector = selector.replace('DkCookie:\n', ' .res $85-(*-ExDispatch),$ea\nDkCookie:\n')
    s = out/'selector.s'
    s.write_text(selector)
    # Bank 65 TRY is the last 8 bytes of the source-declared ProtoArt pad.
    # CHECKED is the last 5 bytes of the selector pad. The bank 85
    # entry/utility ranges sit between Dragon Power code extents D06B/D100.
    # BANK_GATE fits between CV3_GFX_85's C8DC end and Dragon ART C900.
    spans = [('TRY', 65, 0xa738, 8, 0xff), ('EX_SELECT', 65, 0xa740, 0xb0, None),
             ('CHECKED', 65, 0xa7d5, 5, 0xea), ('BANK_GATE', 85, 0xa8dc, 36, 0xff),
             ('BANK_UTIL', 85, 0xb06b, 33, 0xff), ('BANK_ENTRY', 85, 0xb08c, 114, 0xff),
             ('BANK_CODE_HEADER', 85, 0xb8f0, 16, 0xff),
             ('SIDE_GATE', 124, 0xad9b, 51, 0xff), ('SIDE_RETURN', 124, 0xaa7e, 15, 0xea),
             ('RARE_GUARD', 124, 0xa716, 15, 0xea), ('RARE_FOREIGN', 124, 0xa824, 10, 0xea),
             ('RARE_CLASS', 124, 0xa8c7, 15, 0xea), ('RARE_TABLE', 124, 0xa95e, 15, 0xea),
             ('RARE_CONSTANT', 124, 0xab3d, 15, 0xea), ('RARE_FINISH', 124, 0xabd7, 13, 0xea)]
    cfg = out/'selector.cfg'
    cfg.write_text('MEMORY {\n'+''.join(
        f'{name}: start=${pc:04x}, size={size}, file="{(out/(name+".bin")).as_posix()}";\n'
        for name, _, pc, size, _ in spans)+'}\nSEGMENTS {\n'+''.join(
        f'{name}: load={name}, type=ro;\n' for name, *_ in spans)+'}\n')
    assemble([s, R/'tools/reference/mini_mario_idle_fast.s'], cfg, 'resident', labels=True)
    # CHECKED shares the explicitly reserved last 5 selector bytes.
    # Apply its code after verifying the assembled selector keeps that pad.
    for name, bank, pc, size, fill in spans:
        data = (out/(name+'.bin')).read_bytes()
        assert len(data) <= size
        at = 16+bank*8192+(pc&8191)
        if name == 'EX_SELECT':
            old = (owner/'selector-v15.bin').read_bytes()
            assert len(old) == len(data) == size and old[0x95:0x9a] == data[0x95:0x9a] == b'\xea'*5
        else:
            old = bytes([fill])*len(data)
        patch(at, old, data, name)
    patch(16+124*8192+0xad9, bytes.fromhex('8d6a01'), bytes.fromhex('4c9bad'), 'Native side ingress')
    patch(16+124*8192+0x506, bytes.fromhex('8a0a0a'), bytes.fromhex('4c16a7'), 'Rare constants ingress')

    # A movement callback gets here through complete authentication on its
    # first use in an update. Publish its epoch in cleared Mini private state.
    kernel = KERNEL.with_suffix('.s').read_text()
    before = ' lda FrameCounter\n cmp MiniEpoch\n'
    assert kernel.count(before) == 1
    kernel = kernel.replace(before, ' lda FrameCounter\n sta $c3f0\n cmp MiniEpoch\n')
    asm = out/'mini-idle.s'
    asm.write_text(kernel)
    binary = assemble([asm], KERNEL.with_suffix('.cfg'), 'mini-idle', labels=True)
    old, new = KERNEL.with_suffix('.bin').read_bytes(), binary.read_bytes()
    assert len(new) <= 5120
    start = 1048592+962*1024
    end = start+5120
    patch(start, old.ljust(5120, b'\xff'), new.ljust(5120, b'\xff'), 'Mini kernel')
    cookie = 16+65*8192+0x1003
    art_and_meta = raw[end:end+2048]
    previous = hashlib.sha256(old.ljust(5120,b'\xff')+art_and_meta).digest()[:13]
    updated = hashlib.sha256(raw[start:end+2048]).digest()[:13]
    patch(cookie+3, previous, updated, 'Mini cookie')
    rom = out/'mini-idle-fast.nes'
    rom.write_bytes(raw)
    for ext in ['.lbl', '.dbg']:
        shutil.copyfile(ROM.with_suffix(ext), rom.with_suffix(ext))
    receipt = dict(candidate_SHA256=sha(rom), parent_SHA256=PARENT, kernel_bytes=len(new), patches=patches)
    (out/'candidate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(sha(rom))


if __name__ == '__main__':
    main()
