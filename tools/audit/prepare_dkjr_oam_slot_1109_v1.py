"""Repair DK Jr's rotated logical OAM allocation without growing its overlay."""
from pathlib import Path
import json
import re
import subprocess

import audit_dkjr_installed_ingress_1108_v1 as I

R, N, F = I.R, I.N, I.F
OUT = R / 'build/dkjr-oam-slot-1109-v1'
PRIVATE = R / 'build/dkjr-native-resume-1108/dkjr-private.nes'
PIN = '411a563b46a9d5caf848b9efb7ec3d592cf1aa5c8c5062175d6512865f42841b'
CURRENT = R / 'build/mini-busy-pipeline-final-1108/candidate.nes'
MINI_PRIVATE = R / 'build/mini-parser-lift-1109/candidate.nes'
SOURCES = I.BASE / 'native-entrance-v89.s'
PAYLOAD = I.BASE / 'native-payload-v90.bin'
DESCRIPTOR = I.BASE / 'native-combined-owner-v101-measurement.json'
TRACE = R / 'build/dkjr-render-trace-1108/capture/result.json'
sha = I.sha


def replace_once(src, a, b):
    assert src.count(a) == 1, a
    return src.replace(a, b)


def assemble(stem, src):
    base = OUT / stem
    srcfile = base.with_suffix('.s')
    cfgfile = base.with_suffix('.cfg')
    labels = base.with_suffix('.lbl')
    obj = base.with_suffix('.o')
    binary = base.with_suffix('.bin')
    cfg = (I.BASE / 'native-entrance-v89.cfg').read_text()
    cfg = re.sub(r'file="[^"]*/native-entrance-(pause|main|ports)-v89.bin"',
                 lambda m: f'file="{(OUT / (stem + "-" + m[1] + ".bin")).as_posix()}"', cfg)
    srcfile.write_text(src)
    cfgfile.write_text(cfg)
    cc = R / 'tools/Windows/cc65/bin'
    subprocess.run([cc / 'ca65.exe', srcfile, '-o', obj], check=True)
    subprocess.run([cc / 'ld65.exe', '-C', cfgfile, obj, '-o', binary, '-Ln', labels], check=True)
    obj.unlink()
    syms = {name: int(addr, 16) for addr, name in re.findall(r'^al ([0-9A-F]+) \.(\w+)$', labels.read_text(), re.M)}
    return binary.read_bytes(), syms


def source():
    old = SOURCES.read_text()
    # Export only audit labels. This must first reproduce the frozen image.
    labels = '.export DkjrNativeBodyEnd,DkEmitNo,BodyValidate,BodyWrite,DkEffectPalette\n'
    old = labels + old
    body = old.split('\nDkjrNativeDrawBody:\n', 1)[1].split('\nDkjrNativeBodyEnd:', 1)[0]
    effect = old.split('\nDkEmitEffectPair:\n', 1)[1].split('\nDkNativeEffectsEnd:', 1)[0]
    new_body = replace_once(body, 'DkShortCandidate211:\n jeq BodyDrawDone\n', '')
    new_body = replace_once(new_body, ' cpy #241', ' cpy #240')
    new_body = replace_once(new_body, ''' lda GuestOamRotationActive
 beq :+
 lda RgOamRotation
 and #3
DkShortCandidate214:
 bne BodyDrawDone
:
 ldx #0''', ' ldx #0')
    new_body = replace_once(new_body, ' bcs BodyDrawDone\n clc\n adc #8', ' bcs BodyDrawDone\n adc #8')
    new_body = replace_once(new_body, ''' and #1
DkShortCandidate218:
 bne BodyDrawDone
 lda $c211,x
 clc
 adc #1''', ''' tay
 and #1
DkShortCandidate218:
 bne BodyDrawDone
 iny
 tya''')
    new_body = replace_once(new_body, ''' bne BodyDrawDone
 txa
 clc
 adc #8
 tax
 cpx #32
 bne BodyValidate
 ldx #0
BodyWrite:''', ''' bne BodyDrawDone
 txa
 adc #7                     ; last compare was equal, C=1
 tax
 cpx #32
 bne BodyValidate
 ldy CurrentOAMOffset
 jsr DkRotateOAMY
 bcs BodyDrawDone
 ldx #0
BodyWrite:''')
    new_body = replace_once(new_body, ''' sty CurrentOAMOffset
 inc DrawBodyResult''', ''' lda CurrentOAMOffset
 adc #15                    ; final CPX #32 sets C, the end is logical
 sta CurrentOAMOffset
 inc DrawBodyResult''')
    new_effect = replace_once(effect, ' beq DkEmitNo\n tya', ' cpy #252\n bcs DkEmitNo\n tya')
    new_effect = replace_once(new_effect, ''' bcs DkEmitNo
 lda WTop
 sta Sprite_Data,y''', ''' bcs DkEmitNo
 jsr DkRotateOAMY
 bcs DkEmitNo
 lda WTop
 sta Sprite_Data,y''')
    new_effect = replace_once(new_effect, ' tya\n clc\n adc #4\n sta CurrentOAMOffset',
                              ' lda CurrentOAMOffset\n adc #4\n sta CurrentOAMOffset')
    new = replace_once(old, body, new_body)
    new = replace_once(new, effect, new_effect)
    for label in ('DkShortCandidate211', 'DkShortCandidate214'):
        new = replace_once(new, ',' + label + ',', ',')
    old_gate = ''' lda GuestOamRotationActive
 beq DkEffectsAligned
 lda RgOamRotation
 and #3
 jne DkEffectsDone
DkEffectsAligned:'''
    new = replace_once(new, old_gate, '')
    # Reclaim only local arithmetic. No source effect selector/atlas changes.
    new = replace_once(new, ''' cmp #9
 bcs DkHangingNext
 and #3
 bne DkHangingNext
 lda $c42c,x
 sec
 sbc #$4c''', ''' cmp #9
 bcs DkHangingNext
 tay
 and #3
 bne DkHangingNext
 tya
 adc #$58                   ; C=0 from CMP #9, convert A4-based to 4C-based
'''.rstrip())
    new = replace_once(new, ' lda $c428,x\n sec\n sbc #1\n sta WTop', ' ldy $c428,x\n dey\n sty WTop')
    new = replace_once(new, ''' cmp #$b0
 bcs DkFallingNext
 and #1
 bne DkFallingNext
 lda $c201,x
 clc
 adc #1''', ''' cmp #$b0
 bcs DkFallingNext
 tay
 and #1
 bne DkFallingNext
 iny
 tya''')
    new = replace_once(new, ' lda $c201,x\n sec\n sbc #$24', ' lda $c201,x\n sbc #$24')
    new = replace_once(new, ''' cmp #$94
 bcs DkFindPoint
 sec
 sbc #$90
 asl
 clc
 adc #$8c''', ''' cmp #$94
 bcs DkFindPoint
 asl
 adc #$6b                   ; ASL($90..$93) yields $20..$26 with C=1''')
    rotate = '''DkRotateOAMY:
 lda GuestOamRotationActive
 beq @ready
 tya
 clc
 adc RgOamRotation
 tay
 and #3
 bne @bad
@ready:
 clc
 rts
@bad:
 sec
 rts
'''
    return old, new, rotate


def images():
    original_source, new_source, rotation = source()
    base, old_symbols = assemble('old-linked', original_source)
    payload = PAYLOAD.read_bytes()
    assert len(payload) == 11*1024 and len(base) == 0x1fe0 and payload[:len(base)] == base
    body_at = old_symbols['DkjrNativeBodyEnd']
    fx_at = old_symbols['DkNativeEffectsEnd']
    # The source-owned leaf entries and the following ABI stay pinned. The
    # internal effects helper and its local tables may move inside their leaf.
    new_source = replace_once(new_source, '\nDkjrNativeBodyEnd:',
                              f'\n.res ${body_at-old_symbols["DkjrNativeDrawBody"]:x}-(*-DkjrNativeDrawBody),$ea\nDkjrNativeBodyEnd:')
    new_source = replace_once(new_source, '\nDkNativeEffectsEnd:',
                              '\n' + rotation + f'.res ${fx_at-old_symbols["DkNativeDraw"]:x}-(*-DkNativeDraw),$ea\nDkNativeEffectsEnd:')
    candidate, symbols = assemble('new-linked', new_source)
    ranges = [(old_symbols['DkjrNativeDrawBody'], body_at), (old_symbols['DkNativeDraw'], fx_at)]
    assert all(symbols[name] == old_symbols[name] for name in ('DkjrNativeDrawBody', 'DkjrNativeBodyEnd', 'DkNativeDraw', 'DkNativeEffectsEnd'))
    assert len(base) == len(candidate) and all(any(lo <= 0xa000+i < hi for lo, hi in ranges)
                                             for i, (a,b) in enumerate(zip(base, candidate)) if a != b)
    return payload, candidate + payload[len(candidate):], ranges, symbols


def manifest_rows(old, new):
    descriptor = json.loads(DESCRIPTOR.read_text())
    pages = [row['physical_CHR'] for row in descriptor['patches'] if 'physical_CHR' in row]
    assert len(pages) == 11
    patches = []
    for i, page in enumerate(pages):
        old_page = old[i*1024:(i+1)*1024]
        new_page = new[i*1024:(i+1)*1024]
        if old_page != new_page:
            patches.append(dict(physical_CHR=page, file_offset=1048592+page*1024,
                                old_hex=old_page.hex(), new_hex=new_page.hex()))
    old_cookie = (I.BASE/'native-cookie-v90.bin').read_bytes()
    assert old_cookie == bytes([0xa7, 40, 1]) + bytes.fromhex(sha(old))[:13]
    new_cookie = old_cookie[:3] + bytes.fromhex(sha(new))[:13]
    cookie_pc = 0xa7c5
    patches.append(dict(physical_PRG=65, CPU_half_open=[cookie_pc, cookie_pc+16],
                        file_offset=16+65*8192+cookie_pc-0xa000,
                        old_hex=old_cookie.hex(), new_hex=new_cookie.hex()))
    return patches


def compose(raw, patches):
    image = bytearray(raw)
    for row in patches:
        at = row['file_offset']
        old, new = (bytes.fromhex(row[k]) for k in ('old_hex', 'new_hex'))
        assert raw[at:at+len(old)] == old and len(old) == len(new)
        image[at:at+len(new)] = new
    return bytes(image)


def main():
    OUT.mkdir(exist_ok=True)
    raw = PRIVATE.read_bytes()
    assert sha(raw) == PIN
    trace = json.loads(TRACE.read_text())
    assert trace['ROM_sha256'] == PIN and trace['body']['returns'] == 116 and trace['body']['writes'] == 0
    old, new, ranges, labels = images()
    patches = manifest_rows(old, new)
    targets = [(PRIVATE, PIN), (CURRENT, '37bb9c1a69b993edda540c75cbe256aeac75396d55d34d9daf3d4de86deebeeb'),
               (MINI_PRIVATE, 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2')]
    hashes = {}
    for target, pin in targets:
        parent = target.read_bytes()
        assert sha(parent) == pin
        hashes[pin] = sha(compose(parent, patches))
    receipt = dict(passed=True, CPU_only=True, CPU_execution_pending=True, ROM_written=False,
                   base_SHA256=PIN, source_render_extents=ranges, patches=patches, memory_only_hashes=hashes,
                   labels={n: labels[n] for n in ('DkjrNativeDrawBody','BodyValidate','BodyWrite','DkNativeDraw',
                                                'DkEmitEffectPair','DkEmitNo','DkNativeEffectsEnd')},
                   bindings={str(p):sha(p.read_bytes()) for p in [Path(__file__), SOURCES, PAYLOAD, DESCRIPTOR, TRACE]})
    (OUT/'oam-source.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(ranges, hashes, flush=True)


if __name__ == '__main__':
    main()
