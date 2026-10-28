"""Sparse queued-HP successor on adopted5a; no install/native launch."""
from pathlib import Path
import difflib
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
B = R/'build'
sys.path.insert(0, str(R/'tools/audit'))
from kirby_icon_palette_build_v1 import command, link
from check_tmnt_audio_fallback_oc import qualified
from current_roster_compact_11_v1 import linked
sys.path.insert(0, str(R/'tools'))
from prepare_cv3_dmc_mirror import prepare

OLD = '5a0a37a97e95ce3c1086f91f6000ad0157bb477f923027d39f0342d9389e6db2'
P = 'chip_hud_queue_complete'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

HELPER = '''; Foreground-only, same existing CD_LOGIC bank. No persistent cache/RAM.
; Empty and whole-singleton queues retain fast paths. For longer queues,
; suppress only if the last possibly overlapping complete command is an
; identical current HP packet. Never mutate or remove an existing command.
; A known first HP record seeds the scan without parsing it again.
; All nametable mirrors are treated as potential aliases. Unsupported native
; repeat/vertical/zero256/high aliases or malformed data append conservatively.
.pushseg
.segment "CD_LOGIC"
.proc CdQueueHud
 cpx #0
 bne Nonempty
Append:
__ORIGINAL_APPEND__
 rts
Nonempty:
 cpx #7
 jcc Append
 lda VRAM_Buffer1
 cmp #$20
 bne UnknownFirst
 lda VRAM_Buffer1+1
 cmp #$4b
 bne UnknownFirst
 lda VRAM_Buffer1+2
 cmp #4
 bne UnknownFirst
 lda VRAM_Buffer1+3
 cmp #$24
 bne UnknownFirst
 lda VRAM_Buffer1+4
 cmp CdHudText
 bne UnknownFirst
 lda VRAM_Buffer1+5
 cmp CdHudText+1
 bne UnknownFirst
 lda VRAM_Buffer1+6
 cmp CdHealth
 bne UnknownFirst
 cpx #7
 bne KnownPrefix
 lda VRAM_Buffer1+7
 jne Append
 jmp Suppress
KnownPrefix:
 tya
 pha
 ldx #7
 ldy #1
 jmp Scan
UnknownFirst:
 cpx #7
 jeq Append
 tya
 pha
 ldx #0
 ldy #0
Scan:
 cpx VRAM_Buffer1_Offset
 jeq AtEnd
 jcs Fallback
 txa
 clc
 adc #3
 cmp VRAM_Buffer1_Offset
 jcs Fallback ; header and at least one data byte must fit.
 lda VRAM_Buffer1,x
 cmp #$20
 jcc Fallback
 cmp #$40
 jcs Fallback
 lda VRAM_Buffer1+2,x
 jeq Fallback ; native zero means256, never an empty command.
 and #$c0
 jne Fallback ; retain all repeat/vertical/high-flag packet semantics.
 txa
 clc
 adc VRAM_Buffer1+2,x
 adc #3
 cmp VRAM_Buffer1_Offset
 bcc Bounded
 jne Fallback
Bounded:
 pha ; next complete command index; only scratch is the real CPU stack.
 lda VRAM_Buffer1,x
 and #3
 bne Next
 lda VRAM_Buffer1+1,x
 cmp #$4f
 bcs Next
 clc
 adc VRAM_Buffer1+2,x ; exclusive end; low start<=78 and count<=63.
 cmp #$4c
 bcc Next
 ldy #0 ; any possible mirrored or partial overlap invalidates the prior match.
 lda VRAM_Buffer1,x
 cmp #$20
 bne Next
 lda VRAM_Buffer1+1,x
 cmp #$4b
 bne Next
 lda VRAM_Buffer1+2,x
 cmp #4
 bne Next
 lda VRAM_Buffer1+3,x
 cmp #$24
 bne Next
 lda VRAM_Buffer1+4,x
 cmp CdHudText
 bne Next
 lda VRAM_Buffer1+5,x
 cmp CdHudText+1
 bne Next
 lda VRAM_Buffer1+6,x
 cmp CdHealth
 bne Next
 ldy #1
Next:
 pla
 tax
 jmp Scan
AtEnd:
 lda VRAM_Buffer1,x
 bne Fallback
Finished:
 tya
 tax
 pla
 tay
 txa
 beq RestoreAppend
 jmp Suppress
Fallback:
 ldy #0
 jmp Finished
RestoreAppend:
 ldx VRAM_Buffer1_Offset
 jmp Append
Suppress:
 ldx VRAM_Buffer1_Offset
 lda #0
 clc
 clv ; original bounded offset+7 always clears V.
 rts
.endproc
.popseg
'''


def main():
    parent = B/'kirby-mike-polish-production.nes'
    assert sha(parent) == OLD
    out = B/(P+'.nes')
    assert not out.exists()
    raw, syms, a, loc, _ = linked(parent)
    start = loc('CdHud')
    assert int(syms['CdHud']['size'], 0) == 76
    assert raw[start+24:start+26] == b'\xa9\x20' and raw[start+75] == 0x60
    assert (start-16)//8192 == 79 and raw[16+79*8192+0x98a:16+80*8192] == b'\xff'*(8192-0x98a)
    source = R/'src/chip_dale_health.s'
    original = source.read_bytes()
    text = original.decode()
    at = text.index('.proc CdHud')
    begin = text.index(' lda #$20\r\n', at)
    end = text.index('Done:rts\r\n', begin)
    body = text[begin:end].replace('\r\n', '\n').rstrip('\n')
    replaced = text[:begin]+' jmp CdQueueHud\r\n .res 48,$ea ; retain original Done/text/public PCs.\r\n'+text[end:]
    leaf = B/(P+'_health.s')
    leaf.write_bytes(replaced.encode())
    helper_text = HELPER.replace('__ORIGINAL_APPEND__', body)
    helper = B/(P+'_helper.s')
    helper.write_bytes(helper_text.replace('\n', '\r\n').encode())
    er = (R/'src/entrypoint.s').read_bytes()
    needle = b'.include "chip_dale_health.s"'
    assert er.count(needle) == 1
    entry = B/(P+'_entrypoint.s')
    entry.write_bytes(er.replace(needle, b'.include "'+leaf.name.encode()+b'"')+
        b'\r\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\r\n.include "'+helper.name.encode()+b'"\r\n.endif\r\n')
    template = json.loads((B/'cv3_life_gain_watch_build.json').read_text())['command']
    cmd = command(template, out, entry)
    link(cmd, out)
    prepare(R, out)
    nr = out.read_bytes()
    delta = [i for i, (x, y) in enumerate(zip(raw, nr)) if x != y]
    assert len(raw) == len(nr) and {(i-16)//8192 for i in delta} == {79}
    qo, qn = qualified(parent), qualified(out)
    assert not {k:(v, qn.get(k)) for k,v in qo.items() if qn.get(k) != v}
    _, ns, na, nl, _ = linked(out)
    assert na('CdQueueHud') == 0xa98a and (nl('CdQueueHud')-16)//8192 == 79
    size = int(ns['CdQueueHud']['size'], 0)
    assert raw[nl('CdQueueHud'):nl('CdQueueHud')+size] == b'\xff'*size
    patch = B/(P+'_implementation.patch')
    changes = ''.join(difflib.unified_diff(original.decode().splitlines(True), replaced.splitlines(True),
        fromfile='src/chip_dale_health.s', tofile='src/chip_dale_health.s'))
    changes += ''.join(difflib.unified_diff([], helper_text.splitlines(True), fromfile='/dev/null', tofile='src/chip_hud_queue.s'))
    changes += ''.join(difflib.unified_diff(er.decode().splitlines(True),
        (er.decode()+'\r\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\r\n.include "chip_hud_queue.s"\r\n.endif\r\n').splitlines(True),
        fromfile='src/entrypoint.s', tofile='src/entrypoint.s'))
    patch.write_bytes(changes.encode())
    ordinary = []
    for mapper, want in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                         ('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        dest = B/(P+'_'+mapper+'_flagoff.nes')
        c = command(template, dest, entry, mapper)
        link(c, dest)
        assert sha(dest) == want
        ordinary.append(dict(mapper=mapper, sha256=want, whole_exact=True))
    paths = [Path(__file__),parent,parent.with_suffix('.dbg'),source,R/'src/entrypoint.s',leaf,helper,entry,
        patch,out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),out.with_suffix('.cv3-mirror.json'),
        R/'tools/prepare_cv3_dmc_mirror.py']
    result = dict(passed=True,source_only=True,native_run=False,parent_sha256=OLD,candidate_sha256=sha(out),
        changed_bytes=len(delta),changed_banks=[79],all_other_ROM_header_CHR_bytes_exact=True,
        all_existing_qualified_symbols_exact=True,old_qualified_symbols=len(qo),helper_address='79:A98A',
        helper_bytes=size,new_RAM=0,NMI_changes=0,only_CPU_stack_scratch=True,ordinary=ordinary,
        source_overlay={'src/chip_dale_health.s':str(leaf),'src/chip_hud_queue.s':str(helper)},
        entrypoint_addition='Expanded-MMC5-only final include chip_hud_queue.s; all current5a source retained',
        command=cmd,bindings={str(p):sha(p)for p in paths})
    target = B/(P+'_build.json')
    target.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,ROM_sha256=sha(out),receipt=str(target),sha256=sha(target),changed_bytes=len(delta),helper_bytes=size)))


if __name__ == '__main__':
    main()
